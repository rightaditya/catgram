# catgram
Basic tools for working with categorial grammars

This is a simple Python package providing some basic tools for working with
categorial grammars.
Development is on-again, off-again.
Bug reports and feature requests are welcome—especially if it's for an item on
the [TODO list](#todo) below, as you'd be providing extra motivation! :)

This package also includes a CCG dependency evaluation script that implements
decomposed scoring as specified in [Decomposed scoring of CCG
dependencies](https://aclanthology.org/2023.acl-short.89/).
See [below](#decomposed-scoring) for examples.
If you use decomposed scoring in your research, please cite the paper:
* [Aditya Bhargava](https://www.cs.toronto.edu/~aditya/) and [Gerald
  Penn](https://www.cs.toronto.edu/~gpenn/). 2023. [Decomposed scoring of CCG
  dependencies](https://aclanthology.org/2023.acl-short.89/).  In *Proceedings
  of the 61st Annual Meeting of the Association for Computational Linguistics
  (Volume 2: Short Papers)*, pages 1030–1040, Toronto, Canada.  Association for
  Computational Linguistics.

The script can also do the regular CCG dependency evaluation
([examples](#standard-ccg-scoring)).

In general, if you use this package in your research, please include a link to
[the GitHub repository](https://github.com/rightaditya/catgram), and remember
to cite any appropriate research papers depending on your usage (e.g., for
decomposed scoring as mentioned above; cite [(Lewis and Steedman,
2014)](https://aclanthology.org/D14-1107/) if
you use this package's implementation of their head-finding rules; etc.).

## Requirements

* Python 3.10+
* `lambda_calculus` Python package (will be installed automatically by `pip`
  command below)

## Installation

In your environment of choice:
```shellsession
$ pip3 install catgram
```

If you only want to run the evaluation script, you might want to consider using
[`pipx`](https://pypa.github.io/pipx/) to keep the installation isolated:
```shellsession
$ pipx install catgram
$ ccg_depeval -h
```
Or use it to run the script in a temporary environment:
```shellsession
$ pipx run --spec catgram ccg_depeval -h
```

## Examples

### Decomposed scoring

In additional to subcategorial labelling and alignment, decomposed scoring
specifies the inclusion of root nodes.
Most parsers do not explicitly specify these, and if they do, they must be
extracted from heads specified in the `.auto` file (as far as I know, EasyCCG
is the only parser that does this).
The `ccg_depeval` script includes the facility for extracting root dependencies
as necessary from parser `.auto` files (most statistical CCG parsers at least
have the option to output these).

Usage is as follows:
```shellsession
$ ccg_depeval ground_truth_deps sys_deps ground_truth.auto sys.auto
```
where:
* `ground_truth_deps` is the ground-truth dependencies, usually as produced
  by the `parg2ccgbank_deps` script from C&C (the actual filenames will be
  `wsj00.ccgbank_deps` for the dev set or `wsj23.ccgbank_deps` for the test
  set). The original `PARG` file format from CCGbank can also be used.
* `sys_deps` is the dependencies predicted by a statistical parser, usually as
  produced by the `generate` program from C&C (I recommend using what's
  available in the Java version of C&C as it is updated compared to what's in
  the original C&C package).
* `ground_truth.auto` is the ground-truth `.auto` file (e.g., straight from
  CCGbank). The heads specified in this file are followed directly according
  to the syntax specified in CCGbank.
* `sys.auto` is the parse preidcted by the statistical parser. By default, the
  head-finding rules of [Lewis and Steedman
  (2014)](https://aclanthology.org/D14-1107/) are followed to extract the root
  node.

Note: instead of `.auto` files, you can also provide root node information
directly in a `.roots` file.
The format is as produced by the `ccg_roots` script
([examples](#extracting-roots)).

A warning will be issued if there is no root available for a sentence, including
if the last two arguments aren't specified.
You can use the `-r` option to suppress this warning if you don't want to fuss
with root nodes:
```shellsesion
$ ccg_depeval -r ground_truth_deps sys_deps
```
This can be handy for, e.g., evaluating the Java version of the C&C parser,
which doesn't produce a `.auto` file and instead produces a `.deps` file
directly.
Of course, omitting the root nodes will produce different scores.
See [(Bhargava and Penn, 2023)](https://aclanthology.org/2023.acl-short.89/)
and [(Bhargava, 2022, chapter 5)](https://hdl.handle.net/1807/125446) for
examples of why you should include root nodes.

Other options of the script allow you to control whether subcategorial labelling
and/or alignment are used as well, or to print per-sentence scores. See the
script's help for full details:
```shellsession
$ ccg_depeval -h
```

### Standard CCG scoring

For convenience, you can use the `-s` flag when running `ccg_depeval` to revert
to the standard CCG scoring method:
```shellsession
$ ccg_depeval -s ground_truth_deps sys_deps
```

### Extracting roots

This package also includes a standalone root-extraction script.
For example:
```shellsession
$ ccg_roots -m ls14 sys.auto
will_8 S[dcl]
is_3 S[dcl]
...
```
It's important to use `-m ls14` for a `.auto` file generated by most statistical
parsers and `-m autofile` (which is the same as omitting the `-m` option) for
a `.auto` file where the heads specified as per the `.auto` file syntax are
indeed the desired heads.
The latter case is applicable to CCGbank's `.auto` files but not those produced
by most parsers, since they do not indicate the semantic heads.
(EasyCCG is the biggest exception to this, and indeed, the `ls14` rules are the
same as used by that parser.)
If you use the `ls14` option for something in your research, make sure to cite
[Lewis and Steedman (2014)](https://aclanthology.org/D14-1107/) as Section 3.5
of that paper is where the rules were originally specified.

See the script help for full usage details:
```shellsession
$ ccg_roots -h
```

## TODO

* Tests
* Ability to directly evaluate CCG .auto files
    * This would re-implement the functionality of the `generate` program from
      C&C (or the more directly-integrated version of this process in Java C&C)
      so that new parsers wouldn't need to go back to C&C to do the evaluations
* Examples for basic usage (for `CategoryTree` and `TermGraph`)
    * For now, take a look at [`dependencies.py`](catgram/ccg/dependencies.py)
      for examples of how to use `CategoryTree`.
      If examples are even slightly of interest to you, please submit a GitHub
      issue asking for them as doing so will help motivate me to add them!
* Other tools that might be useful?
    * Evaluation scripts (e.g., for evaluating statistical parsers)
    * Visualization tools (CCG dependency graphs, LCG term graphs; outputs to
      SVG, LaTeX...)

## License

Unless otherwise stated, all files in this package are subject to the below
copyright and license. The main exception is
[candc_ignore.py](catgram/ccg/candc_ignore.py), which is derived from the
original C&C package and thus covered by the C&C System Licence Agreement.
The code therein is reproduced with permission for inclusion in this package.

Copyright 2023 Aditya Bhargava

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
the files in this repository except in compliance with the License. You may
obtain a copy of the License at <https://www.apache.org/licenses/LICENSE-2.0> or
in the [LICENSE](LICENSE) file in this repository.

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
