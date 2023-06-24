# This code in this file is provided under the C&C System License Agreement:
# C&C System Licence Agreement
#
# This Licence Agreement (the "Agreement") is entered, effective this
# date, by and between the "Licensor" (as defined below), and the
# individual executing this Agreement below as "Licensee" (hereinafter,
# the "Licensee").
#
# 1. Licensor hereby grants Licensee a royalty-free, non-exclusive,
# non-transferable licence to use the C&C system (herinafter referred to
# as the "Licensed Software") as follows solely for a Non-Commercial
# Purpose (as defined in paragraph 3 below):
#
#     (a) Licensee may prepare derivative works (the "Derivative Works")
#     which are based on or incorporate all or part of the Licensed
#     Software, including, without limitation, works (the "Adaptations")
#     which
#
#         (i) are translations of all or part of the Licensed Software
#         into different programming languages, or
#         (ii) are revisions, improvements or corrections to all or part
#         of the Licensed Software,
#
# provided that, Licensee shall treat all Derivative Works as Licensed
# Software under this Agreement; and
#
#     (b) Licensee may make only such copies of the Licensed Software as
#     are necessary for Licensee's development of the Derivative Works.
#
# 2. All copies of the Licensed Software and Derivative Works prepared
# in accordance with paragraph 1 shall retain the copyright notice
# appearing in the Licensed Software. If the Licensed Software includes
# computer programs in object code form, Licensee shall not de-compile,
# reverse engineer or disassemble such programs.
#
# 3. As used in this Agreement, "Non-Commercial Purpose" means use of
# the Licensed Software and Derivative Works solely for education or
# research.  "Non-Commercial Purpose" excludes, without limitation, any
# use of the Licensed Software or Derivative Works for, as part of, or
# in any way in connection with a product (including software) or
# service which is sold, offered for sale, licensed, leased, loaned or
# rented.
#
# 4. Licensee shall acknowledge use of the Licensed Software and
# Derivative Works in all publications of research based in whole or in
# part on their use through citation of the following publication:
#
# Parsing the WSJ using CCG and Log-Linear Models
# Stephen Clark and James R. Curran
# Proceedings of the 42nd Annual Meeting of the Association for
# Computational Linguistics (ACL-04), pp. 104-111, Barcelona, Spain 2004
#
# 5. Licensee hereby grants Licensor a non-exclusive, royalty-free, fully
# paid-up, worldwide, perpetual licence to:
#
#     (a) Reproduce, prepare derivative works based on and distribute all
#     or part of the Derivative Works; and
#
#     (b) Make, have made, use, offer to sell, sell, license or import any
#     products (including software) or services under any intellectual
#     property rights owned or licensed by Licensee which relate to
#
#         (i) all or part of the Derivative Works (including as executed
#         by a CPU), or
#         (ii) methods or concepts embodied in, or implemented through
#         the execution by a CPU of, the Derivative Works. Licensee
#         shall provide the contact person (or an alternative contact
#         notified to the Licensee from time to time)
#
# 	candc@it.usyd.edu.au
#
#         with feedback concerning Licensee's Derivative Works and, if
#         requested, provide such persons with source code copies of
#         Licensee's Derivative Works.
#
# 6. This Agreement is personal between Licensor and Licensee. No
# ownership interest in the Licensed Software (or the copy of which is
# provided by Licensor pursuant to paragraph 1) is transferred to
# Licensee. Licensee's interest in the Derivative Works is limited
# solely to Licensee's additions and the Derivative Works are subject in
# their entirety to Licensor's intellectual property rights. Licensor
# may assign or transfer to any company or person, or grant to any
# company or person a licence or sublicence under, all or part of its
# interest in any rights to the Licensed Software, this Agreement, or
# any licence granted to Licensor hereunder. Licensee may not assign or
# sublicense Licensee's rights hereunder.
#
# 7. Licensor may terminate this Agreement at any time by sending
# written notice of termination to Licensee at the address specified
# below.  Termination shall be effective as provided in the
# notice. Unless the notice shall provide otherwise, upon termination,
# Licensee shall destroy all copies of the Licensed Software and
# Derivative Works. Licensee's obligations under this Agreement,
# including any rights granted to Licensor pursuant to paragraph 5,
# shall survive and continue after termination.
#
# 8. Licensor has no obligation to support or maintain the Licensed
# Software and grants Licensee this right to use the Licensed Software
# "AS IS". LICENSEE ASSUMES TOTAL RESPONSIBILITY AND RISK FOR LICENSEE'S
# USE OF THE LICENSED SOFTWARE. LICENSOR DOES NOT MAKE, AND EXPRESSLY
# DISCLAIMS, ANY EXPRESS OR IMPLIED WARRANTIES, REPRESENTATIONS OR
# ENDORSEMENTS OF ANY KIND WHATSOEVER, INCLUDING, WITHOUT LIMITATION,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY, REASONABLE QUALITY OR
# FITNESS FOR A PARTICULAR PURPOSE, AND THE WARRANTIES OF TITLE OR
# NON-INFRINGEMENT. IN NO EVENT SHALL LICENSOR BE LIABLE FOR
#
#     (a) ANY INCIDENTAL, CONSEQUENTIAL, OR INDIRECT DAMAGES, DAMAGES
#     FOR LOSS OF PROFITS, BUSINESS INTERRUPTION, LOSS OF PROGRAMS OR
#     INFORMATION, AND ANY OTHER LOSS OR DAMAGE WHATSOEVER ARISING OUT
#     OF THE USE OF OR INABILITY TO USE THE SOFTWARE, EVEN IF LICENSOR
#     OR ANY OF ITS AUTHORIZED REPRESENTATIVES HAS BEEN ADVISED OF THE
#     POSSIBILITY OF SUCH DAMAGES,
#
#     (b) ANY CLAIM ATTRIBUTABLE TO ERRORS, OMISSIONS, OR OTHER
#     INACCURACIES IN THE SOFTWARE, OR
#
#     (c) ANY CLAIM BY ANY THIRD PARTY.
#
# 9. This Agreement shall be governed by and construed in accordance
# with the laws of England and the English courts shall have exclusive
# jurisdiction.
#
# LICENSOR
# University of Edinburgh
# James R. Curran
# University of Oxford
# University of Sydney

# The contents of this file come from the `evaluate` script included in the
# original C&C package as well as the `evaluate_new` script included in the Java
# C&C package. The code included here has been reproduced with permission for
# inclusion in the `catgram` package.

# These ignored deps are for the markedup file that comes with Java C&C
_ignore_deps_java = set(
    tuple(x.split())
    for x in r"""
rule_id 7
rule_id 11
rule_id 12
rule_id 14
rule_id 15
rule_id 16
rule_id 17
rule_id 51
rule_id 52
rule_id 56
rule_id 91
rule_id 92
rule_id 95
rule_id 96
rule_id 98
conj 1 0
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 0
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 2
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 3
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 6
((S[to]{_}\NP{Y}<1>){_}/(S[b]{Z}\NP{Y}){Z}<2>){_} 1 9
((S[b]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 6
((S[b]{_}\NP{Y}<1>){_}/PP{Z}<2>){_} 1 6
(((S[b]{_}\NP{Y}<1>){_}/PP{Z}<2>){_}/NP{W}<3>){_} 1 6
(S[X]{Y}/S[X]{Y}<1>){_} 1 13
(S[X]{Y}/S[X]{Y}<1>){_} 1 5
(S[X]{Y}/S[X]{Y}<1>){_} 1 55
((S[X]{Y}/S[X]{Y}){Z}\(S[X]{Y}/S[X]{Y}){Z}<1>){_} 2 97
((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_} 2 4
((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_} 2 93
((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_} 2 8
((S[X]{Y}\NP{Z}){Y}/(S[X]{Y}<1>\NP{Z}){Y}){_} 2 94
((S[X]{Y}\NP{Z}){Y}/(S[X]{Y}<1>\NP{Z}){Y}){_} 2 18
been ((S[pt]{_}\NP{Y}<1>){_}/(S[ng]{Z}<2>\NP{Y}){Z}){_} 1 0
been ((S[pt]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 there 0
been ((S[pt]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 There 0
be ((S[b]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 there 0
be ((S[b]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 There 0
been ((S[pt]{_}\NP{Y}<1>){_}/(S[pss]{Z}\NP{Y}){Z}<2>){_} 1 0
been ((S[pt]{_}\NP{Y}<1>){_}/(S[adj]{Z}\NP{Y}){Z}<2>){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[pss]{Z}\NP{Y}){Z}<2>){_} 1 0
have ((S[b]{_}\NP{Y}<1>){_}/(S[pt]{Z}\NP{Y}){Z}<2>){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[adj]{Z}\NP{Y}){Z}<2>){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[ng]{Z}\NP{Y}){Z}<2>){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[pss]{Z}<2>\NP{Y}){Z}){_} 1 0
going ((S[ng]{_}\NP{Y}<1>){_}/(S[to]{Z}<2>\NP{Y}){Z}){_} 1 0
have ((S[b]{_}\NP{Y}<1>){_}/(S[to]{Z}\NP{Y}){Z}<2>){_} 1 0
Here (S[adj]{_}\NP{Y}<1>){_} 1 0
# this is a dependency Julia doesn't have but looks okay
from (((NP{Y}\NP{Y}<1>){_}/(NP{Z}\NP{Z}){W}<3>){_}/NP{V}<2>){_} 1 0
""".strip().split(
        "\n"
    )
    if not x.startswith("#")
)

# And here are the original C&C ones, so that outputs from original C&C's
# `generate` program can be evaluated as well. Note the different format: here
# long-distance labels are indicated with an asterisk, and some of the slots are
# slightly different.
_ignore_deps_orig = set(
    tuple(x.split())
    for x in r"""
rule_id 7
rule_id 11
rule_id 12
rule_id 14
rule_id 15
rule_id 16
rule_id 17
rule_id 51
rule_id 52
rule_id 56
rule_id 91
rule_id 92
rule_id 95
rule_id 96
rule_id 98
conj 1 0
((S[to]{_}\NP{Z}<1>){_}/(S[b]{Y}<2>\NP{Z*}){Y}){_} 1 0
((S[to]{_}\NP{Z}<1>){_}/(S[b]{Y}<2>\NP{Z*}){Y}){_} 1 2
((S[to]{_}\NP{Z}<1>){_}/(S[b]{Y}<2>\NP{Z*}){Y}){_} 1 3
((S[to]{_}\NP{Z}<1>){_}/(S[b]{Y}<2>\NP{Z*}){Y}){_} 1 6
((S[to]{_}\NP{Z}<1>){_}/(S[b]{Y}<2>\NP{Z*}){Y}){_} 1 9
((S[b]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 6
((S[b]{_}\NP{Y}<1>){_}/PP{Z}<2>){_} 1 6
(((S[b]{_}\NP{Y}<1>){_}/PP{Z}<2>){_}/NP{W}<3>){_} 1 6
(S[X]{Y}/S[X]{Y}<1>){_} 1 13
(S[X]{Y}/S[X]{Y}<1>){_} 1 5
(S[X]{Y}/S[X]{Y}<1>){_} 1 55
((S[X]{Y}/S[X]{Y}){Z}\(S[X]{Y}/S[X]{Y}){Z}<1>){_} 2 97
((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_} 2 4
((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_} 2 93
((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_} 2 8
((S[X]{Y}\NP{Z}){Y}/(S[X]{Y}<1>\NP{Z}){Y}){_} 2 94
((S[X]{Y}\NP{Z}){Y}/(S[X]{Y}<1>\NP{Z}){Y}){_} 2 18
been ((S[pt]{_}\NP{Y}<1>){_}/(S[ng]{Z}<2>\NP{Y*}){Z}){_} 1 0
been ((S[pt]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 there 0
been ((S[pt]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 There 0
be ((S[b]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 there 0
be ((S[b]{_}\NP{Y}<1>){_}/NP{Z}<2>){_} 1 There 0
been ((S[pt]{_}\NP{Y}<1>){_}/(S[pss]{Z}<2>\NP{Y*}){Z}){_} 1 0
been ((S[pt]{_}\NP{Y}<1>){_}/(S[adj]{Z}<2>\NP{Y*}){Z}){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[pss]{Z}<2>\NP{Y*}){Z}){_} 1 0
have ((S[b]{_}\NP{Y}<1>){_}/(S[pt]{Z}<2>\NP{Y*}){Z}){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[adj]{Z}<2>\NP{Y*}){Z}){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[ng]{Z}<2>\NP{Y*}){Z}){_} 1 0
be ((S[b]{_}\NP{Y}<1>){_}/(S[pss]{Z}<2>\NP{Y*}){Z}){_} 1 0
going ((S[ng]{_}\NP{Y}<1>){_}/(S[to]{Z}<2>\NP{Y*}){Z}){_} 1 0
have ((S[b]{_}\NP{Y}<1>){_}/(S[to]{Z}<2>\NP{Y*}){Z}){_} 1 0
Here (S[adj]{_}\NP{Y}<1>){_} 1 0
# this is a dependency Julia doesn't have but looks okay
from (((NP{Y}\NP{Y}<1>){_}/(NP{Z}\NP{Z}){W}<3>){_}/NP{V}<2>){_} 1 0
""".strip().split(
        "\n"
    )
    if not x.startswith("#")
)

deps_to_ignore = _ignore_deps_java | _ignore_deps_orig


def ignore_dep(pred: str, cat: str, slot: str, arg: str, rule_id: str):
    # TODO: document
    return (
        ("rule_id", rule_id) in deps_to_ignore
        or (cat, slot, rule_id) in deps_to_ignore
        or (pred, cat, slot, rule_id) in deps_to_ignore
        or (pred, cat, slot, arg, rule_id) in deps_to_ignore
    )
