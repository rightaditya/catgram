from collections import abc
from contextlib import nullcontext
from functools import partial
from pathlib import Path
import re
from string import punctuation
from typing import NamedTuple, Optional

from catgram.category_tree import CategoryTree


punctuation = set(punctuation) - set(r"\/()[]")
node_re = re.compile(r"\(<([TL]) ([^ >]+) ([^ >]+)(?: ([^ >]+?)){,4} ([^ >]+?)>")
brackets_re = re.compile(r"[LR][RC]B")
feat_re = re.compile(r"\[[a-z]+]")
slash_re = re.compile(r"\\/")


class WordToken(NamedTuple):
    # "token" here means unique occurence of a token in the sentence (as in the
    # type-token distinction), *not* the new-school meaning of "piece that goes
    # into neural language model"
    word: str
    idx: int

    def __str__(self) -> str:
        return "_".join(map(str, self))

    @classmethod
    def from_str(cls, s: str) -> "WordToken":
        word, idx = s.split("_")
        return cls(word, int(idx))


class HeadDependency(NamedTuple):
    token: WordToken
    cat: CategoryTree

    def __str__(self) -> str:
        return " ".join(map(str, self))

    @classmethod
    def from_str(cls, s: str) -> Optional["HeadDependency"]:
        if s == str(None):
            return None
        token, cat = s.split(" ")
        return cls(WordToken.from_str(token), CategoryTree.from_str(cat))


class _MalformedAutoTreeError(Exception):
    pass


def _head_autofile(
    it: abc.Iterator[re.Match], idx: int = 0, head_idx: int = 3, word_idx: int = 4
) -> tuple[HeadDependency, int]:
    # just follow the head specified by the relevant field in CCGbank's .auto
    # format. AFAIK only CCGbank uses this field for a semantic head; most
    # parsers just use it for the syntactic head that can otherwise be easily
    # determined from the input and output functors (at least for the
    # CCG-proper rules). the main exception is EasyCCG, which is the parser
    # associated with Lewis and Steedman (2014), which follows the head-finding
    # rules specified in that paper and implemented in _head_ls14
    m = next(it)
    node_cat = CategoryTree.from_str(re.sub(r"\[conj]$", "", m[2]))
    match m[1]:
        case "T":
            (head_l, _), idx = _head_autofile(it, idx)
            if m[5] == "2":
                (head_r, _), idx = _head_autofile(it, idx)
                return HeadDependency([head_l, head_r][int(m[head_idx])], node_cat), idx
            elif m[5] == "1":
                return HeadDependency(head_l, node_cat), idx
        case "L":
            idx += 1
            return (
                HeadDependency(
                    WordToken(slash_re.sub("/", m[word_idx]), idx), node_cat
                ),
                idx,
            )
    raise _MalformedAutoTreeError()


def _head_ls14(
    it: abc.Iterator[re.Match], idx: int = 0, head_idx: int = 3, word_idx: int = 4
) -> tuple[HeadDependency, int]:
    m = next(it)
    node_cat_str = re.sub(r"\[X]", "", m[2])  # for C&C
    node_cat = CategoryTree.from_str(node_cat_str)
    match m[1]:
        case "T":
            (head_l, cat_l), idx = _head_ls14(it, idx, head_idx, word_idx)
            if m[5] == "2":
                (head_r, cat_r), idx = _head_ls14(it, idx, head_idx, word_idx)
                cat_l_s, cat_r_s = str(cat_l), str(cat_r)
                if "conj" in node_cat_str and (
                    "conj" not in cat_l_s or "conj" not in cat_r_s
                ):
                    raise ValueError("'conj' parent nodes must have 'conj' children")
                if set(cat_l_s) & punctuation or brackets_re.match(cat_l_s):
                    if set(cat_r_s) & punctuation or brackets_re.match(cat_r_s):
                        # when both children are punctuation categories, choose
                        # the one that matches the parent as head, preferring
                        # the left child if both do
                        if node_cat_str == cat_l_s:
                            return HeadDependency(head_l, node_cat), idx
                        if node_cat_str == cat_r_s:
                            return HeadDependency(head_r, node_cat), idx
                        raise ValueError(
                            "one child must project to parent when both "
                            "children are punctuation categories"
                        )
                    # return non-punctuation child as head
                    return HeadDependency(head_r, node_cat), idx
                if set(cat_r_s) & punctuation or brackets_re.match(cat_r_s):
                    # return non-punctuation child as head
                    return HeadDependency(head_l, node_cat), idx
                if "conj" in cat_l_s:
                    if "conj" in cat_r_s:
                        if "conj" not in node_cat_str:
                            raise ValueError(
                                "two 'conj' children must combine to a 'conj' parent"
                            )
                    else:
                        # return non-conj child as head
                        return HeadDependency(head_r, node_cat), idx
                if "conj" in cat_r_s and "conj" not in cat_l_s:
                    raise ValueError(
                        "right child can be 'conj' only when left and parent "
                        "are also 'conj'"
                    )

                # for non-punct/conj cases, default to setting the head to the
                # principal/primary functor, but use the subordinate/secondary
                # functor if the principal looks like adjunction or like it was
                # produced by forward type-raising
                node_nf = CategoryTree.from_str(feat_re.sub("", node_cat_str))
                catl_nf = CategoryTree.from_str(feat_re.sub("", cat_l_s))
                catr_nf = CategoryTree.from_str(feat_re.sub("", cat_r_s))
                if catl_nf.root == "/":
                    if (
                        (catl_nf.result == node_nf and catl_nf.argument == catr_nf)
                        or (
                            catr_nf.root == node_nf.root == "/"
                            and catl_nf.result == node_nf.result
                            and catr_nf.argument == node_nf.argument
                            and catl_nf.argument == catr_nf.result
                        )
                        or (
                            catr_nf.root == node_nf.root
                            and node_nf.result is not None
                            and catr_nf.result.root == node_nf.result.root == "/"
                            and catl_nf.result == node_nf.result.result
                            and catr_nf.argument == node_nf.argument
                            and catr_nf.result.argument == node_nf.result.argument
                            and catl_nf.argument == catr_nf.result.result
                        )
                    ):
                        # A/ or B/ or B2/ or xB2/
                        if (cat_l.result == cat_l.argument) or (
                            cat_l.argument.root == "\\"
                            and cat_l.result == cat_l.argument.result
                        ):
                            # X/X or X/(X\Y)
                            return HeadDependency(head_r, node_cat), idx
                        return HeadDependency(head_l, node_cat), idx
                    if (
                        node_nf.root == catl_nf.root == catr_nf.root == "/"
                        and node_nf.argument == catl_nf.argument == catr_nf.argument
                        and catr_nf.result.root == "\\"
                        and catr_nf.result.argument == catl_nf.result
                        and catr_nf.result.result == node_nf.result
                    ):
                        # xS\
                        return HeadDependency(head_r, node_cat), idx
                if catr_nf.root == "\\":
                    if (
                        (catr_nf.result == node_nf and catr_nf.argument == catl_nf)
                        or (
                            catl_nf.root == node_nf.root
                            and node_nf.result is not None
                            and catr_nf.result == node_nf.result
                            and catl_nf.argument == node_nf.argument
                            and catr_nf.argument == catl_nf.result
                        )
                        or (
                            catl_nf.root == node_nf.root
                            and node_nf.result is not None
                            and catl_nf.result.root == node_nf.result.root == "/"
                            and catr_nf.result == node_nf.result.result
                            and catl_nf.argument == node_nf.argument
                            and catl_nf.result.argument == node_nf.result.argument
                            and catr_nf.argument == catl_nf.result.result
                        )
                    ):
                        # A\ or B\ or xB\ or xB2\
                        if (cat_r.result == cat_r.argument) or (
                            cat_r.argument.root == "/"
                            and cat_r.result == cat_r.argument.result
                        ):
                            # X\X or X\(X/Y)
                            return HeadDependency(head_l, node_cat), idx
                        return HeadDependency(head_r, node_cat), idx
            elif m[5] == "1":
                return HeadDependency(head_l, node_cat), idx
        case "L":
            idx += 1
            return (
                HeadDependency(
                    WordToken(slash_re.sub("/", m[word_idx]), idx), node_cat
                ),
                idx,
            )
    raise _MalformedAutoTreeError()


def parse_head(auto: str, method: str, *, autox: bool = False) -> HeadDependency:
    """
    Get the head of a node in a tree in CCGbank's .auto format (including
    DepCCG's .autox variation).

    Args:
        auto (str): The .auto tree node to find the head of.
        method (str): The head-finding method to use. Options are 'autofile',
            which follows the head specification syntax as defined by CCGbank,
            and 'ls14', which follows the head-finding algorithm rules of
            Lewis and Steedman (EMNLP 2014; i.e., those of EasyCCG) for use with
            other parsers.
        autox (bool, optional): Whether `auto` is in DepCCG's .autox format.
            Defaults to False.

    Raises:
        ValueError: If `method` is not a valid head-finding method.
        ValueError: If `auto` is malformed.
        ValueError: If the head-finding method throws an error.

    Returns:
        HeadDependency: The head of the node in `auto` as found by `method`.
    """
    try:
        _parse_head = globals()[f"_head_{method}"]
    except KeyError:
        raise ValueError(f"Unknown head-finding method: {method!r}") from None
    if autox:
        _parse_head = partial(_parse_head, head_idx=4, word_idx=3)

    try:
        head, _ = _parse_head(it := node_re.finditer(auto))
    except _MalformedAutoTreeError:
        raise ValueError(f"Malformed .auto tree: {auto!r}") from None
    except Exception:
        raise ValueError(f"Error in parsing .auto tree: {auto!r}")
    try:
        next(it)
    except StopIteration:
        pass
    else:
        raise ValueError(f"Malformed .auto tree: {auto!r}")

    return head


def parse_roots(
    auto: abc.Iterable[str] | Path | str,
    method: str,
    autox: bool = False,
) -> abc.Generator[HeadDependency | None, None, None]:
    """Find the root of each sentence in CCGbank's .auto format.

    Args:
        auto (abc.Iterable[str] | Path | str): The sentences to find the roots
            of or the path to a file containing the sentences.
        method (str): The head-finding method to use. See `get_head` for
            options.
        autox (bool, optional): Whether `auto` is in DepCCG's .autox format.
            Defaults to False.

    Yields:
        HeadDependency | None: The root of each given sentence.
    """
    with open(auto) if isinstance(auto, (Path, str)) else nullcontext(auto) as auto:
        for line in auto:
            line = line.strip()
            if line.startswith("ID="):
                continue
            elif not line:
                yield None
                continue
            yield parse_head(line, method, autox=autox)


head_methods = []
for name in list(globals()):
    if name.startswith("_head_"):
        head_methods.append(name[6:])
