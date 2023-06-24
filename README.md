# catgram
Basic tools for working with categorial grammars

This is a simple Python package providing some basic tools for working with
categorial grammars.
Development is on-again, off-again.
Issue reports and requests welcome—even if it's for an item on the [TODO
list](#todo) below, as you'd be providing extra motivation! :)

This package also includes a CCG dependency evaluation script that implements
decomposed scoring as specified in [Decomposed scoring of CCG
dependencies](https://www.cs.toronto.edu/~aditya/ccgdspaper).

## Requirements

* Python 3.10+
* `lambda_calculus` Python package (will be installed automatically by `pip`
  command below)

## Installation

In your environment of choice:
```shellsession
$ pip3 install catgram
```

## TODO

* Tests
* Better documentation, I guess...
    * Examples
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
obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0> or
in the [LICENSE](LICENSE) file in this repository.

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
