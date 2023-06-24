from dataclasses import dataclass
from functools import cache, cached_property
import logging
import re
from typing import ClassVar, overload, Optional

try:
    from typing import Self  # Python 3.11+
except ImportError:
    from typing import TypeAlias

    Self: TypeAlias = "CategoryTree"


@dataclass(frozen=True, repr=False)
class CategoryTree:
    """A tree representation of a category."""

    atom_re: ClassVar[re.Pattern] = re.compile(r"^[^\s/\\()]+$")
    atom_delim: ClassVar[re.Pattern] = re.compile(r"([()\\/])")

    root: str
    result: Optional[Self] = None
    argument: Optional[Self] = None

    def __post_init__(self: Self):
        # validate the fields' values
        if not isinstance(self.root, str):
            raise TypeError(f"root must be {str} instance; got {self.root!r}")
        if self.result is None:
            if self.argument is not None:
                raise ValueError("argument without result")
            if not self.atom_re.fullmatch(self.root):
                raise ValueError(
                    f"atomic category must not have spaces, slashes, "
                    f"backslashes, or parentheses; got {self.root!r}"
                )
        else:
            if self.argument is None:
                raise ValueError("result without argument")
            for _child in ("result", "argument"):
                if not isinstance(child := getattr(self, _child), cls := type(self)):
                    raise TypeError(
                        f"{_child} must be a {cls.__name__} instance; got {child!r}"
                    )
            if self.root not in {"/", "\\"}:
                raise ValueError(
                    f"root for complex category must be '/' or '\\'; "
                    f"got {self.root!r}"
                )

    @classmethod
    def from_str(
        cls,
        cat: str,
        left_associative: bool = False,
        lambek: bool = False,
        strict: bool = True,
    ) -> Self:
        """
        Convert a string representation of a category to a CategoryTree.

        Args:
            cat (str): The category in string form.
            left_associative (bool, optional): Whether the category is
                left-associative (alternative is full parenthesization).
                Defaults to `False` (full parenthesization).
            lambek (bool, optional): Whether the category is in Lambek order
                (alternative is Steedman order). Defaults to `False` (
                Steedman order).
            strict (bool, optional): Whether to be strict when parsing the
                string (alternative is to make some simple assumptions to try
                to parse certain malformed categories). Defaults to `True`.
                `False` can be useful for categories predicted by a
                constructive supertagger if it might have minor malformations
                that can be straightforwardly corrected.

        Returns:
            CategorTree: The CategoryTree representation of the input category.
        """
        if (key := (cat, lambek)) in INSTANCES:
            return INSTANCES[key]
        cat_ = tuple(a for a in cls.atom_delim.split(cat) if a)
        return cls._parse_str(cat_, left_associative, lambek, strict)[0]

    @classmethod
    def _parse_str(
        cls,
        cat: tuple[str],
        l_assoc: bool,
        lambek: bool,
        strict: bool,
        idx: int = 0,
        in_paren: bool = False,
    ) -> tuple[Self, int]:
        root = left = right = None
        i = idx
        while i < len(cat):
            if not isinstance(cat[i], str):
                raise TypeError(
                    f"category must be str; got {cat[i]!r} at " f"index {i}"
                )
            if cat[i] == ")":
                if not in_paren:
                    msg = (
                        f'xtraneous closing parenthesis in "{"".join(cat)}" '
                        f"at index {i}"
                    )
                    if strict:
                        raise MalformedCategoryError(f"E{msg}")
                    logging.warning(f"Ignoring e{msg}")
                break
            if right is not None:
                if not l_assoc or cat[i] not in "/\\":
                    # only valid case for iterating after having read a right
                    # node is reading a closing paren, which was handled above
                    if not in_paren or strict:
                        raise MalformedCategoryError(
                            f'Extraneous stuff "{cat[i]}" in "{"".join(cat)}" '
                            f"at index {i} after right node "
                            f'"{str(right)}": {cat[i]}'
                        )
                    # if being lenient (not strict), allow some leeway if in
                    # parenthetical
                    logging.warning(
                        f"Assuming missing closing parenthesis in "
                        f'"{"".join(cat)}" at index {i}'
                    )
                    i -= 1  # unconsume this token
                    break
            if cat[i] in "/\\":
                c_str = "".join(cat[idx:i])
                if root is None:
                    raise MalformedCategoryError(
                        f'Missing left node in "{"".join(cat)}" '
                        f'before "{cat[i]}" at index {i}'
                    )
                if left is None:
                    if isinstance(root, cls):
                        left = root
                    else:
                        if (c_str, lambek) in INSTANCES:
                            left = INSTANCES[c_str, lambek]
                            # TODO: nix sanity check after adding some tests
                            assert left == cls(root)
                        else:
                            INSTANCES[c_str, lambek] = left = cls(root)
                elif not l_assoc or right is None:
                    # TODO: I suspect this case should be "and", not "or", but
                    #  at least this way it's overzealous rather than lax
                    raise MalformedCategoryError(
                        f'Two consecutive slashes in "{"".join(cat)}" at index "{i}"'
                    )
                else:
                    # build a tree from existing root, left, right and assign
                    # to left
                    if (key := (c_str, lambek)) in INSTANCES:
                        left = INSTANCES[key]
                        # TODO: nix sanity check after adding some tests
                        if lambek and root == "\\":
                            assert left == cls(root, right, left)
                        else:
                            assert left == cls(root, left, right)
                    elif lambek and root == "\\":
                        INSTANCES[key] = left = cls(root, right, left)
                    else:
                        INSTANCES[key] = left = cls(root, left, right)
                    right = None
                root = cat[i]
            else:
                p = cat[i]
                if p == "(":
                    p, i = cls._parse_str(
                        cat, l_assoc, lambek, strict, idx=i + 1, in_paren=True
                    )

                if left is None:
                    if root is not None:
                        raise MalformedCategoryError(
                            f'Extraneous stuff in "{"".join(cat)}" at index '
                            f'{i} after "{root}"; expected slash'
                        )
                    if l_assoc and isinstance(p, cls):
                        raise MalformedCategoryError(
                            "Parenthesized expression in left-associative "
                            f'mode in "{"".join(cat)}" at index {i} before slash'
                        )
                    root = p
                else:
                    if not isinstance(p, cls):
                        if (key := (p, lambek)) in INSTANCES:
                            p = INSTANCES[key]
                            # TODO: nix sanity check after adding some tests
                            assert p == cls(key[0])
                        else:
                            INSTANCES[key] = p = cls(p)
                    right = p
            i += 1
        else:
            if in_paren:
                msg = f'nclosed parenthetical in "{"".join(cat)}" at index {i}'
                if strict:
                    raise MalformedCategoryError(f"U{msg}")
                logging.warning(f"Ignoring u{msg}")
        if root is None:
            raise MalformedCategoryError("Empty category")

        cat_ = "".join(cat[idx:i])
        if isinstance(root, cls):
            logging.warning(f'Stripping redundant parentheses in "{cat_}"')
            cat_ = cat_[1:-1]
            # TODO: nix sanity check after adding some tests
            assert root == INSTANCES[cat_, lambek]
            return root, i
        if root in "/\\" and right is None:
            raise MalformedCategoryError(
                f'Missing right node after "{root}" at index {i} in "{cat_}"'
            )

        key = cat_, lambek
        if key in INSTANCES:
            cat_ = INSTANCES[key]
            # TODO: nix sanity check after adding some tests
            if lambek and root == "\\":
                assert cat_ == cls(root, right, left)
            else:
                assert cat_ == cls(root, left, right)
        elif lambek and root == "\\":
            INSTANCES[key] = cat_ = cls(root, right, left)
        else:
            INSTANCES[key] = cat_ = cls(root, left, right)

        return cat_, i

    @cached_property
    def is_complex(self: Self) -> bool:
        """Whether this category is complex (i.e., not atomic)."""
        return not self.is_atomic

    @cached_property
    def is_atomic(self: Self) -> bool:
        """Whether this category is atomic (i.e., takes no arguments)."""
        return self.result is None

    @cached_property
    def target(self: Self) -> str | None:
        """
        The target atomic category of a complex category (i.e., the result of
        the result of the result ... of the category until the result is
        atomic).
        """
        if self.is_atomic:
            return None
        if self.result.is_atomic:
            return self.result.root
        return self.result.target

    @cached_property
    def arity(self: Self) -> int:
        """
        The number of arguments this category takes before yielding its target
        (atomic) category.
        """
        return 0 if self.is_atomic else self.result.arity + 1

    @cached_property
    def _len(self: Self) -> int:
        """
        The number of atomic categories in this category (i.e., number of leaf
        nodes in tree).
        """
        if self.is_atomic:
            return 1
        return len(self.result) + len(self.argument)

    def __len__(self: Self) -> int:
        """
        The number of atomic categories in this category (i.e., number of leaf
        nodes in tree).
        """
        return self._len

    @cached_property
    def degree(self: Self) -> int:
        """Category tree height plus one, as defined by Moot and Retoré (2012)."""
        if self.is_atomic:
            return 1  # would be 0 for binary tree depth
        return max(self.result.degree, self.argument.degree) + 1

    @cached_property
    def order(self: Self) -> int:
        """A measure of highest "complexity" of this category's arguments."""
        if self.is_atomic:
            return 0
        return max(self.result.order, self.argument.order + 1)

    @cached_property
    def size(self: Self) -> int:
        """Number of nodes in this category tree."""
        if self.is_atomic:
            return 1
        return self.result.size + self.argument.size + 1

    def __str__(self: Self) -> str:
        """
        Fully-parenthesized string representation of this category in Steedman
        order.
        """
        return self.to_str()

    @overload
    def to_str(
        self: Self,
        *,
        pol_start: None = ...,
        positive: bool = ...,
        l_assoc: bool = ...,
        lambek: bool = ...,
    ) -> str:
        ...

    @overload
    def to_str(
        self: Self,
        *,
        pol_start: int,
        positive: bool = ...,
        l_assoc: bool = ...,
        lambek: bool = ...,
    ) -> tuple[str, int]:
        ...

    def to_str(
        self: Self,
        *,
        pol_start: int | None = None,
        positive: bool = False,
        l_assoc: bool = False,
        lambek: bool = False,
    ) -> str | tuple[str, int]:
        """String representation of this category

        Args:
            pol_start: If not None, add an index to each atomic category
                that indicates the position of that (polarized) primitive in
                the lexical decomposition of the category. The integer value of
                this parameter specifies the offset to use for the first index.
            positive: Whether the category has positive polarity. Has no effect
                if `pol_start_idx` is None.
            l_assoc: Whether to use left-associative notation
            lambek: Whether to use Lambek notation
        Returns:
            If `pol_start_idx` is None, returns a string representation of this
            category according to the specified notation. If `pol_start_idx` is
            not None, returns a 2-tuple: the first element is the string
            representation of this category and the second element is the final
            atomic index used for this category.
        """
        seq_, pol_idx = self._inorder(l_assoc, lambek, positive)
        if pol_start is None:
            return "".join(seq_)

        seq = list(seq_)
        leaf_idxs = [i for i, s in enumerate(seq) if not self.atom_delim.fullmatch(s)]
        # TODO: nix sanity check after adding some tests
        assert len(leaf_idxs) == len(self) == len(pol_idx)
        # for i, l in enumerate(leaf_idxs, start=pol_start):
        #    seq[l] = f"{seq[l]}_{i}"
        for i, j in zip(leaf_idxs, pol_idx, strict=True):
            seq[i] = f"{seq_[i]}_{pol_start + j}"
        return "".join(seq), pol_start + len(leaf_idxs)

    def __repr__(self: Self) -> str:
        # cls = self.__class__.__name__
        # if self.is_atomic:
        #    return f"{cls}({self.root})"
        # return (
        #     f"{cls}(result={self.result!r}, root={self.root}, "
        #     f"argument={self.argument!r})"
        # )
        # The above can get pretty long for larger categories, so just use the
        # string representation wrapped in the class name.
        return f"{self.__class__.__name__}({self.to_str()})"

    @cache
    def _inorder(
        self: Self, l_assoc: bool, lambek: bool, positive: bool
    ) -> tuple[tuple[str, ...], tuple[int, ...]]:
        if self.is_atomic:
            return (self.root,), (0,)
        result, result_idxs = self.result._inorder(l_assoc, lambek, positive)
        argument, argument_idxs = self.argument._inorder(l_assoc, lambek, not positive)
        if not l_assoc and len(result) > 1:
            result = ("(", *result, ")")
        if len(argument) > 1:
            argument = ("(", *argument, ")")

        if (self.root == "/") == positive:
            offset = len(argument_idxs)
            result_idxs = tuple(i + offset for i in result_idxs)
        else:
            offset = len(result_idxs)
            argument_idxs = tuple(i + offset for i in argument_idxs)

        if lambek and self.root == "\\":
            return argument + (self.root,) + result, argument_idxs + result_idxs
        return result + (self.root,) + argument, result_idxs + argument_idxs

    @cached_property
    def func_seq(self: Self) -> tuple[str, ...]:
        """
        The functorial sequence that this category decomposes into, as defined
        by Bhargava and Penn (ACL 2023).
        """
        if self.is_atomic:
            return (self.root,)
        argument_str = self.argument.to_str()
        if self.argument.is_atomic:
            argument_str = f"{self.root}{argument_str}"
        else:
            argument_str = f"{self.root}({argument_str})"
        return self.result.func_seq + (argument_str,)

    @cache
    def get_arg(self: Self, slot: int) -> Self:
        if slot > self.arity:
            raise ValueError(
                f"invalid slot {slot!r} for category {self} with arity {self.arity}"
            )
        if slot == self.arity:
            return self.argument if slot else self
        return self.result.get_arg(slot)


class MalformedCategoryError(Exception):
    pass


INSTANCES: dict[tuple[str, bool], CategoryTree] = {}
