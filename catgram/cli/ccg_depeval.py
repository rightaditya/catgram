#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import abc
import csv
from pathlib import Path
from sys import stdout

from catgram.ccg.dependencies import DependencyScores, file_deps, score_sentence
from catgram.ccg.heads import HeadDependency, parse_roots, head_methods


def _roots_iter(
    file: Path, method: str
) -> abc.Generator[HeadDependency | None, None, None]:
    if file.name.endswith(".roots"):
        with open(file) as f:
            for line in f:
                yield HeadDependency.from_str(line.strip())
    else:
        yield from parse_roots(file, method, file.name.endswith(".autox"))


def main():
    parser = ArgumentParser(
        description="Scoring of CCGbank-style dependencies",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "truth",
        type=Path,
        help="ground truth dependencies file",
    )
    parser.add_argument(
        "eval",
        type=Path,
        help="dependencies file to evaluate",
    )
    parser.add_argument(
        "truth_roots",
        nargs="?",
        type=Path,
        help="ground-truth roots file or .auto file to extract roots from",
    )
    parser.add_argument(
        "eval_roots",
        nargs="?",
        type=Path,
        help="evaluation roots file or .auto file to extract roots from",
    )
    parser.add_argument(
        "--no-subcat",
        "-c",
        action="store_false",
        dest="subcat",
        help="disable subcategorial labelling (and alignment)",
    )
    parser.add_argument(
        "--no-subcat-align",
        "-a",
        action="store_false",
        dest="subcat_align",
        help="disable subcategorial alignment",
    )
    parser.add_argument(
        "--root-method",
        "-m",
        choices=head_methods,
        default=head_methods[1],
        help="head-finding method for predicted dependencies; "
        f"'{head_methods[0]}' follows the head specified by the .auto tree "
        "format, which is only applicable for CCGbank ground truth or EasyCCG "
        f"predictions; '{head_methods[1]}' follows the head-finding rules of "
        "Lewis and Steedman (EMNLP 2014; i.e., those of EasyCCG) for use with "
        "other parsers; ignored if reading from .roots file",
    )
    parser.add_argument(
        "--ignore-roots",
        "-r",
        action="store_true",
        help="ignore root dependencies if present in the input and do not warn"
        " about their absence if not",
    )
    parser.add_argument(
        "--std",
        "-s",
        action="store_true",
        help="use original CCGbank evaluation; equivalent to -car",
    )
    parser.add_argument(
        "--unlabelled",
        "-u",
        action="store_true",
        help="use unlabelled scoring",
    )
    parser.add_argument(
        "--tsv",
        "-t",
        action="store_true",
        help="output in TSV format",
    )
    parser.add_argument(
        "--each-sentence",
        "-e",
        action="store_true",
        help="output metrics for each sentence; implies -t",
    )

    args = parser.parse_args()
    if args.std:
        args.subcat = args.subcat_align = False
        args.ignore_roots = True
    if args.unlabelled:
        labelling = None
    else:
        labelling = "subcat" if args.subcat else "full"
    if args.each_sentence:
        args.tsv = True

    n_correct = n_tru = n_hyp = 0

    if args.truth_roots:
        args.truth_roots = _roots_iter(args.truth_roots, head_methods[0])
    if args.eval_roots:
        args.eval_roots = _roots_iter(args.eval_roots, args.root_method)
    if args.tsv:
        writer = csv.writer(stdout, delimiter="\t", lineterminator="\n")
        if args.each_sentence:
            writer.writerow(["sent_id", *DependencyScores._fields])
        else:
            writer.writerow(DependencyScores._fields)

    i = 1
    for tru_deps, hyp_deps in zip(
        file_deps(args.truth, args.truth_roots),
        file_deps(args.eval, args.eval_roots),
        strict=True,
    ):
        scores = score_sentence(
            tru_deps,
            hyp_deps,
            labelling=labelling,
            subcat_align=args.subcat_align,
            ignore_root=args.ignore_roots,
            sentence_id=f"#{i}",
        )
        if args.each_sentence:
            writer.writerow([i, *scores])
        i += 1
        n_tru += scores.n_deps_tru
        n_hyp += scores.n_deps_hyp
        n_correct += scores.correct

    if n_tru == n_hyp == 0:
        precision = recall = f1 = 1.0
    else:
        precision = n_correct / n_hyp if n_hyp else 0.0
        recall = n_correct / n_tru if n_tru else 0.0
        f1 = 2 * n_correct / (n_tru + n_hyp)
    if not args.each_sentence:
        if args.tsv:
            writer.writerow([n_tru, n_hyp, n_correct, precision, recall, f1])
        else:
            print(f"Precision: {precision:.1%}\nRecall: {recall:.1%}\nF1: {f1:.1%}")


if __name__ == "__main__":
    main()
