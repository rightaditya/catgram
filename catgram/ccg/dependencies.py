from collections import abc
from functools import cache
from itertools import repeat
import logging
from pathlib import Path
import re
from typing import Any, NamedTuple, TypeAlias

from catgram.category_tree import CategoryTree
from catgram.ccg.candc_ignore import ignore_dep
from catgram.ccg.heads import HeadDependency, WordToken


logger = logging.getLogger("catgram.ccg.dependencies")


class DependencyEdge(NamedTuple):
    pred: WordToken
    arg: WordToken


class DependencyLabel(NamedTuple):
    cat: CategoryTree
    slot: int


class DependencyScores(NamedTuple):
    n_deps_tru: int
    n_deps_hyp: int
    correct: int
    precision: float
    recall: float
    f1: float


DependencySet: TypeAlias = dict[DependencyEdge, DependencyLabel]


class _LevState(NamedTuple):
    distance: int
    back: tuple[tuple[int, int], ...]
    is_match: bool


@cache
def _lev_matches(
    tru: abc.Sequence[str], hyp: abc.Sequence[str]
) -> frozenset[tuple[int, int]]:
    tru = (*tru, "<end>")
    hyp = (*hyp, "<end>")
    # numpy would be convenient, but i'd prefer to avoid the additional
    # dependency just for this evaluation script; plus this way i can store
    # backpointers and match status for each position
    d = {}
    # technically there should be backpointers in the first row and column but
    # since the ultimate interest is in optimal match states, this row/column
    # will just be ignored for the backward pass
    for i in range(len(tru) + 1):
        d[i, 0] = _LevState(i, (), False)
    for j in range(1, len(hyp) + 1):
        d[0, j] = _LevState(j, (), False)
    for i, t in enumerate(tru, start=1):
        for j, h in enumerate(hyp, start=1):
            sub = 0 if t == h else 1
            dist = min(
                d_del := d[i - 1, j].distance + 1,
                d_ins := d[i, j - 1].distance + 1,
                d_sub := d[i - 1, j - 1].distance + sub,
            )
            back = []
            if i > 1 and j > 1:
                if dist == d_del:
                    back.append((i - 1, j))
                if dist == d_ins:
                    back.append((i, j - 1))
                if dist == d_sub:
                    back.append((i - 1, j - 1))
            d[i, j] = _LevState(dist, tuple(back), sub == 0)

    # and now the backward pass
    lev_matches = set()
    stack = list(d[len(tru), len(hyp)].back)
    while stack:
        i, j = stack.pop()
        state = d[i, j]
        if state.is_match:
            lev_matches.add((i - 1, j - 1))
        stack.extend(state.back)
    return frozenset(lev_matches)


def dep_label_correct(
    tru_label: DependencyLabel,
    hyp_label: DependencyLabel,
    subcat_label: bool,
    subcat_align: bool,
) -> bool:
    """Determine whether the label for a single dependency is correct.

    Note that label correctness is a symmetric measure, but the convention is to
    consider the first set of dependencies to be ground truth so that the
    score meanings are clear.

    Args:
        tru_label (DependencyLabel): The ground-truth dependency label.
        hyp_label (DependencyLabel): The predicted dependency label.
        subcat_label (bool): Whether to use subcategorial labelling as defined
            by Bhargava and Penn (ACL 2023) as opposed to standard,
            full-category labelling.
        subcat_align (bool): Whether to use subcategorial alignment as defined
            by Bhargava and Penn (ACL 2023). Has no effect if `subcat_label` is
            False.

    Returns:
        bool: True if the label is correct according to the specified scoring
            attributes, False otherwise.
    """
    if not subcat_label:
        # no subcategorial labelling, so the full label labels must be equal
        return tru_label == hyp_label
    tru_subcat = tru_label.cat.get_arg(tru_label.slot)
    hyp_subcat = hyp_label.cat.get_arg(hyp_label.slot)
    if tru_subcat != hyp_subcat:
        # if the subcategorial label is incorrect, there's no recovering...
        return False
    # subcategorial label is correct
    if tru_label.slot == hyp_label.slot:
        # slot is correct, no need to think about alignment
        return True
    # subcategorial label is correct but slot is incorrect
    elif not subcat_align:
        # no alignment to accommodate incorrect slot, so label is incorrect
        return False
    # subcategorial label is correct but slot is incorrect; try to find
    # plausible alignment
    tru_fs, hyp_fs = tru_label.cat.func_seq, hyp_label.cat.func_seq
    return (tru_label.slot, hyp_label.slot) in _lev_matches(tru_fs, hyp_fs)


def score_sentence(
    tru_deps: DependencySet,
    hyp_deps: DependencySet,
    *,
    labelling: str | None = "subcat",
    subcat_align: bool = True,
    ignore_root: bool = False,
    sentence_id: Any = None,
) -> DependencyScores:
    """Score the dependencies of a single sentence.

    Note that the score is a symmetric measure, but the convention is to
    consider the first set of dependencies to be ground truth so that the
    meaning of precision and recall is clear.

    Args:
        tru_deps (DependencySet): The ground-truth dependency set.
        hyp_deps (DependencySet): The predicted dependency set.
        labelling (str | None, optional): The labelling method. Can be one of
            'subcat', 'full', or None. 'subcat' is subcategorial labelling as
            defined by Bhargava and Penn (ACL 2023), 'full' is standard,
            full-category labelling as in the standard CCG evaluation, and
            None is no labelling (for computing unlabelled scores). Defaults to
            "subcat".
        subcat_align (bool, optional): Whether to use subcategorial alignment
            as defined by Bhargava and Penn (ACL 2023). Has no effect if
            `labelling` is not 'subcat'. Defaults to True.
        ignore_root (bool, optional): Ignore root dependencies that are in the
            dependency sets and supress warnings about missing root
            dependencies. Defaults to False.
        sentence_id (Any, optional): A label for this sentence. Only used for
            identifying the sentence when issuing warnings. Defaults to None.

    Raises:
        ValueError: If `labelling` is not one of 'subcat', 'full', or None.

    Returns:
        DependencyScores: A named tuple containing relevant scores and counts
            for the given pair of dependency sets. The tuple includes precision,
            recall, and F1, though beware that when evaluating on a corpus of
            sentences, they should not be used as the standard evaluation is
            a micro-average (i.e., computed from aggregated counts rather than
            averaging per-sentence scores).
    """
    if ignore_root:
        tru_deps = {k: v for k, v in tru_deps.items() if k.pred != ("ROOT", 0)}
        hyp_deps = {k: v for k, v in hyp_deps.items() if k.pred != ("ROOT", 0)}
    else:
        if sentence_id is None or sentence_id == "":
            sent_suffix = ""
        else:
            sent_suffix = f" for sentence {sentence_id}"
        if tru_deps and ("ROOT", 0) not in [edge[0] for edge in tru_deps]:
            logger.warning(f"No root in ground-truth dependencies{sent_suffix}")
        if hyp_deps and ("ROOT", 0) not in [edge[0] for edge in hyp_deps]:
            logger.warning(f"No root in predicted dependencies{sent_suffix}")
    n_tru, n_hyp = len(tru_deps), len(hyp_deps)
    if (n_tru == n_hyp == 0) or (
        n_tru == n_hyp == 1
        and list(tru_deps)[0].pred == list(hyp_deps)[0].pred == ("ROOT", 0)
    ):
        # if there are no (non-ROOT) dependencies, score like the standard CCG
        # evaluation (zero contribution to micro-averaged stats); but it doesn't
        # make sense to say precision/recall/F1 are zero for such sentences
        # the most important thing is that the scores are consistent between the
        # case with roots and the case without so that, when compared, the
        # difference doesn't result in treating the case as a rank inversion
        return DependencyScores(
            n_deps_tru=0, n_deps_hyp=0, correct=0, precision=1.0, recall=1.0, f1=1.0
        )
    tru_edges, hyp_edges = set(tru_deps), set(hyp_deps)
    correct_edges = tru_edges & hyp_edges  # start from unlabelled F1
    match labelling:
        case "full" | "subcat":
            correct_edges = {
                e
                for e in correct_edges
                if dep_label_correct(
                    tru_deps[e], hyp_deps[e], labelling == "subcat", subcat_align
                )
            }
        case None:
            pass
        case _:
            raise ValueError(
                "`labelling` must be one of None, 'full', or 'subcat'; "
                f"received {labelling:r}"
            )

    n_correct = len(correct_edges)
    return DependencyScores(
        n_deps_tru=n_tru,
        n_deps_hyp=n_hyp,
        correct=n_correct,
        precision=n_correct / n_hyp if n_hyp else 0.0,
        recall=n_correct / n_tru if n_tru else 0.0,
        f1=2 * n_correct / (n_tru + n_hyp),
    )


def file_deps(
    fn: Path | str, roots: abc.Iterator[HeadDependency | None] | None = None
) -> abc.Generator[DependencySet, None, None]:
    """Read CCG dependencies from a file.

    Args:
        fn (Path | str): The name of the file to read. Accepted formats are
            .deps files produced by Java C&C or C&C's `generate` program (run on
            .auto files produced by a system), CCGbank .parg files, and
            .ccgbank_deps files produced by the `parg2ccgbank_deps` script from
            C&C.
        roots (abc.Iterator[HeadDependency | None] | None, optional): An
            iterator of root dependencies to add to each sentence's dependency
            set. If None, no root dependencies are added. Defaults to None.

    Raises:
        ValueError: If the (optional) commented lines at top of the file aren't
            separated from the rest of the file by a blank line.
        ValueError: If a line has an unexpected number of fields.

    Yields:
        DependencySet: The dependency set for each sentence in the file.
    """
    with open(fn) as f:
        # most files have some comments at the top (indicating the command that
        # produced them, etc.), so test for those while still allowing for
        # a file without them
        if (pre := f.read(2))[0] == "#":
            f.seek(0)
            while line := next(f).strip():
                if line[0] != "#":
                    raise ValueError(
                        f"Unexpected uncommented line at top of {fn}: {line}"
                    )
        else:
            f.seek(0)
        parg = pre == "<s"

        sent_deps = {}
        roots_ = repeat(None) if roots is None else roots
        for line in f:
            if line[:3] == "<c>":
                # skip C&C's POS/category tag line
                continue
            elif parg and line[:2] == "<s":
                # reading CCGbank PARG file, skip sentence start line
                continue
            fields = line.strip().split()
            if not fields or fields[0] == "<\\s>":
                try:
                    root = next(roots_)
                except StopIteration:
                    raise ValueError(
                        "Not enough roots provided for sentences"
                    ) from None
                if root is not None:
                    root_token, root_cat = root
                    sent_deps[
                        DependencyEdge(WordToken("ROOT", 0), root_token)
                    ] = DependencyLabel(root_cat, 0)
                yield sent_deps
                sent_deps = {}
                continue

            if parg and 5 < len(fields) < 8:
                # direct from CCGbank PARG files
                arg_idx, pred_idx, cat, slot, arg, pred = fields[:6]
                pred = WordToken(pred, int(pred_idx) + 1)
                arg = WordToken(arg, int(arg_idx) + 1)
                # pred_idx = int(pred_idx) + 1
                # arg_idx = int(arg_idx) + 1
            else:
                if 4 < len(fields) < 7:
                    # from direct system outputs (e.g., Java C&C) or using C&C's
                    # `generate` program on `.auto` file produced by system
                    pred, cat, slot, arg, rule = fields[:5]
                    if ignore_dep(
                        pred.split("_")[0], cat, slot, arg.split("_")[0], rule
                    ):
                        continue
                    # remove the markup
                    cat = re.sub(r"<[0-9]>|\{[A-Z_]\*?\}|\[X\]", "", cat)[1:-1]
                elif len(fields) == 4:
                    # from CCGbank PARG files that were converted to ccgbank_deps
                    # files using the `parg2ccgbank_deps` script from C&C
                    pred, cat, slot, arg = fields
                else:
                    raise ValueError(f"Unexpected number of fields in line: {line}")
                pred = WordToken.from_str(pred)
                arg = WordToken.from_str(arg)
                # pred, pred_idx = pred.split("_")
                # arg, arg_idx = arg.split("_")
                # pred_idx = int(pred_idx)
                # arg_idx = int(arg_idx)

            # pred = WordToken(pred, pred_idx)
            # arg = WordToken(arg, arg_idx)
            cat = CategoryTree.from_str(cat)
            slot = int(slot)
            sent_deps[DependencyEdge(pred, arg)] = DependencyLabel(cat, slot)
    if roots is not None:
        try:
            next(roots_)
        except StopIteration:
            pass
        else:
            raise ValueError("More roots provided than sentences")
