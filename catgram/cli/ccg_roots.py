#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
from sys import stdin

from catgram.ccg.heads import head_methods, parse_roots


def main():
    parser = ArgumentParser(
        description="Extract roots from CCGbank-style .auto files",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "auto",
        nargs="?",
        type=FileType("r"),
        default=stdin,
        help=".auto file from which to extract heads",
    )
    # TODO: if a new head-finding method is added, the descriptions of each
    #  should go somewhere centralized so that the text can be used here
    #  and elsewhere as needed while staying consistent. an alternative option
    #  would be to put the add_argument call in a dedicated function that
    #  can then be imported elsewhere as needed (assuming the only use is
    #  for CLI param parsing)
    parser.add_argument(
        "--method",
        "-m",
        choices=head_methods,
        default=head_methods[0],
        help="head-finding method; 'autofile' follows the head specified by "
        "the .auto tree format, which is only applicable for CCGbank ground "
        "truth or EasyCCG predictions; 'ls14' follows the head-finding rules "
        "of Lewis and Steedman (EMNLP 2014; i.e., those of EasyCCG) for use "
        "with other parsers",
    )
    parser.add_argument(
        "--autox",
        "-x",
        action="store_true",
        help="force treatment of input file as an .autox file (as produced by "
        "DepCCG)",
    )

    args = parser.parse_args()

    if args.auto.name.endswith(".autox"):
        args.autox = True
    for head_dep in parse_roots(args.auto, args.method, args.autox):
        print(head_dep)


if __name__ == "__main__":
    main()
