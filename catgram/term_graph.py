from collections.abc import Mapping, Sequence
from functools import cache
import re
from typing import NamedTuple

try:
    from typing import Self  # Python 3.11+
except ImportError:
    from typing import TypeAlias

    Self: TypeAlias = "LexicalDecomposition"

from lambda_calculus import terms

from catgram import CategoryTree


class ProofFrameNode(NamedTuple):
    """
    A node in a proof frame.

    * The `atom` field is the (atomic) category label for the node (e.g.,
      `'S'`, `'NP'`, `'N'`, etc.).
    * The `positive` field indicates node polarity (`true` for positive,
      `false` for negative).
    * The `children` field is a tuple of integers indicating the *relative*
      positions of the node's children.

    This type is a tuple; immutability allows instances to be used as values in
    a cache such that lexical categories can re-use nodes and construct new
    ones without altering nodes used for other categories.
    """

    atom: str
    positive: bool
    children: tuple[int, ...] = tuple()

    def __repr__(self):
        return f"{self.atom}{'+' if self.positive else '-'}{self.children}"


class LexicalDecomposition(NamedTuple):
    """
    The result of decomposing a polarized lexical category.

    * The `nodes` field is a tuple of `ProofFrameNode`s, storing them in the
      order indicated by the decomposition rules.
    * The `edges` field is a tuple of integer 2-tuples, indicating the source
      and destination indices of the nodes (as in the `nodes` tuple) for each
      edge (regular or Lambek) as constructed by the lexical decomposition.
    * The `target` field is the index of the node in the `nodes` tuple
      corresponding to the "target" atom of the lexical category. The target
      node is the root node of the lexical decomposition. In constructing
      semantic terms in term graphs, token labels are assigned to target atoms.
    """

    nodes: tuple[ProofFrameNode, ...]
    edges: tuple[tuple[int, int], ...]
    target: int

    @classmethod
    @cache
    def decompose_category(cls, category: CategoryTree, positive: bool = False) -> Self:
        """
        Decompose a polarized lexical category according to the lexical
        decomposition rules.

        Args:
            category (CategoryTree): The lexical category to decompose.
            positive (bool, optional): The polarity of the category. Defaults
                to `False`.

        Returns:
            LexicalDecomposition: The decomposition result.

        Raises:
            ValueError: If the category is not atomic and doesn't have a
                forward or backward slash as its root or if `positive` is
                something other than `True` or `False`.
        """
        if category.is_atomic:
            return cls((ProofFrameNode(category.root, positive),), tuple(), 0)
        result = cls.decompose_category(category.result, positive)
        argument = cls.decompose_category(category.argument, not positive)
        target = result.nodes[result.target]

        match category.root, positive:
            # This is a bit of a mess, but tracking the children here makes the
            # traversal in TermGraph._get_term() much cleaner
            case ("/", False) | ("\\", True):
                shift = len(result.nodes)
                edge = (result.target, shift + argument.target)
                nodes = list(result.nodes)
                nodes[result.target] = nodes[result.target]._replace(
                    children=(edge[1] - edge[0],) + target.children
                )
                left = result._replace(nodes=tuple(nodes))
                right = argument
                # left, right = result, argument
            case ("/", True) | ("\\", False):
                shift = len(argument.nodes)
                edge = (shift + result.target, argument.target)
                left = argument
                nodes = list(result.nodes)
                nodes[result.target] = nodes[result.target]._replace(
                    children=(edge[1] - edge[0],) + target.children
                )
                right = result._replace(nodes=tuple(nodes))
                # left, right = argument, result
            case _:
                raise ValueError(f"invalid category: {category}")

        nodes = left.nodes + right.nodes
        edges = [
            edge,
            *left.edges,
            *[(src + shift, dst + shift) for src, dst in right.edges],
        ]

        return cls(nodes, tuple(edges), edge[0])


class TermGraph:
    """
    A representation of the term graph of a sequent in the Lambek calculus.
    See Fowler (2016) for details.
    """

    # lambda_calculus doesn't like these letters, but doesn't put the list
    # anywhere (it just shows up as a literal in the code)
    _unsafe = re.compile(r"[().λ]")

    def __init__(
        self,
        categories: Sequence[CategoryTree | str | None],
        *,
        sentential: int | None = -1,
        linkage: Mapping[int, int] | None = None,
        words: Sequence | None = None,
    ):
        """
        Construct a term graph for the given sequent and linkage with optional
        token labels.

        Args:
            categories: A `Sequence` of any combination of `CategoryTree`s,
                `str`s, and `None`s. Strings are converted to `CategoryTree`s
                and `None` categories can be useful for representing words with
                no lexical category, a convention sometimes used for some
                punctuation (e.g., in LCGbank).
            sentential (int | None): The index of the sentential category.
                Can be negative as per the usual Python negative-index
                convention. Defaults to `-1`. `None` indicates that there is no
                sentential category.
            linkage: A `Mapping` of source (positive) atom indices to
                destination (negative) atom indices indicating links in the
                term graph.
            words: A `Sequence` of labels used to label lexical categories'
                target atoms.

        Raises:
            ValueError: If `words` is not None and has a different length than
                `categories`.
        """
        self.categories = [
            CategoryTree.from_str(cat) if isinstance(cat, str) else cat
            for cat in categories
        ]
        self.sentential = sentential
        if self.sentential is not None:
            self.sentential = self.sentential % len(self.categories)
        self.linkage = {} if linkage is None else linkage
        self.words = [f"<w_{i}>" for i in range(len(categories))]
        if words is not None:
            if len(words) != len(categories):
                raise ValueError("number of words must match number of categories")
            for i, word in enumerate(words):
                word = self._unsafe.sub("", word)
                if word:
                    self.words[i] = f"{word}_{i}"

        self.decomps = []
        for i, cat in enumerate(self.categories):
            if cat is None:
                self.decomps.append(None)
                continue
            else:
                self.decomps.append(
                    LexicalDecomposition.decompose_category(cat, i == self.sentential)
                )
        self.nodes = []
        self.clens = []
        for decomp in self.decomps:
            self.clens.append(len(self.nodes))
            if decomp is None:
                continue
            self.nodes.extend(decomp.nodes)

        self.labels = [f"{node.atom}_{idx}" for idx, node in enumerate(self.nodes)]
        for word, decomp, clen in zip(
            self.words, self.decomps, self.clens, strict=True
        ):
            if decomp is None:
                continue
            self.labels[clen + decomp.target] = word

    def get_term(self, idx: int | None = None) -> terms.Term:
        """
        Get the semantic term for the token at the given index. The term will
        be beta-normal.

        Args:
            idx (int | None): The index for the token. If `None`, the
                sentential term is returned. Defaults to `None`.

        Returns:
            Term: the semantic term for the token as situated in the term
                graph. If the index provided is that of the sentential category
                and `self` is a valid term graph, this will return the semantic
                term for the entire sentence.

        Raises:
            ValueError: If `idx` is `None` and `self` was not instantiated with
                a sentential category index.
        """
        if idx is None:
            if self.sentential is None:
                raise ValueError(
                    "no sentential category index specified during "
                    "TermGraph instantiation"
                )
            idx = self.sentential

        return self._get_term(self.clens[idx] + self.decomps[idx].target)

    def _get_term(self, idx: int) -> terms.Term:
        if (node := self.nodes[idx]).positive:
            try:
                linked = self.linkage[idx]
            except KeyError:
                term = terms.Variable.with_valid_name(self.labels[idx])
            else:
                term = self._get_term(linked)
            for child in reversed(node.children):
                term = terms.Abstraction(self.labels[idx + child], term)
        else:
            term = terms.Variable.with_valid_name(self.labels[idx])
            for child in node.children:
                term = terms.Application(term, self._get_term(idx + child))

        return term
