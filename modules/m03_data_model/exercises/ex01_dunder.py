"""Exercise 01 — dunder methods: make your types behave like built-ins.

Two classes. `Money` is a value object; `Inventory` is a container. Between
them they cover the dunders you'll write most often in real code.

Run:  uv run pytest modules/m03_data_model/tests/test_ex01_dunder.py -x -q

Constraints:
  * Binary operators return `NotImplemented` for unsupported types — never
    raise TypeError yourself for a *type* mismatch. (A *currency* mismatch is
    a domain rule, and there you DO raise.)
  * `__eq__` and `__hash__` must agree.
  * Use `functools.total_ordering` on Money rather than writing four methods.
"""

import functools
from collections.abc import Iterator, Mapping


@functools.total_ordering
class Money:
    """An amount of money in minor units (cents), with a currency.

    Immutable by convention: no method mutates self; operations return new
    Money instances.

        >>> Money(1050)
        Money(1050, 'USD')
        >>> str(Money(1050))
        '10.50 USD'
        >>> Money(500) + Money(250)
        Money(750, 'USD')
    """

    __slots__ = ("amount", "currency")

    amount: int
    currency: str

    def __init__(self, amount: int, currency: str = "USD") -> None:
        """Store the amount and the normalized (uppercased) currency code.

        Raises:
            ValueError: if currency is not exactly 3 alphabetic characters.
                Include the offending value in the message.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """Unambiguous, and looks like the code that recreates it.

        >>> repr(Money(1050, "eur"))
        "Money(1050, 'EUR')"
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """Human readable: major units with 2 decimals, then the code.

        >>> str(Money(-1050))
        '-10.50 USD'
        """
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Equal when both amount and currency match.

        Return NotImplemented for non-Money operands so Python can fall back.
        """
        raise NotImplementedError

    def __hash__(self) -> int:
        """Must agree with __eq__ — hash the same fields it compares."""
        raise NotImplementedError

    def __lt__(self, other: object) -> bool:
        """Order by amount. total_ordering derives <=, >, >= from this.

        Return NotImplemented for non-Money operands.

        Raises:
            TypeError: if the currencies differ — comparing USD to EUR is
                meaningless, and that IS a domain rule worth enforcing.
        """
        raise NotImplementedError

    def __add__(self, other: object) -> "Money":
        """Add two Money values of the same currency.

        Returns NotImplemented for non-Money operands.

        Raises:
            TypeError: on a currency mismatch.
        """
        raise NotImplementedError

    def __sub__(self, other: object) -> "Money":
        """Subtract, with the same rules as __add__."""
        raise NotImplementedError

    def __mul__(self, factor: object) -> "Money":
        """Multiply by a whole number of units.

        Accept `int` only — and note that `bool` is a subclass of `int`, so
        `Money(100) * True` must be rejected. Return NotImplemented for
        anything else (including float).
        """
        raise NotImplementedError

    def __rmul__(self, factor: object) -> "Money":
        """Handle `3 * money` as well as `money * 3`.

        Hint: this is the one-liner `__rmul__ = __mul__` in the class body,
        but write it as a real method so the stub signature stays honest.
        """
        raise NotImplementedError

    def __neg__(self) -> "Money":
        """Unary minus: -Money(100) == Money(-100)."""
        raise NotImplementedError

    def __abs__(self) -> "Money":
        """abs(Money(-100)) == Money(100)."""
        raise NotImplementedError

    def __bool__(self) -> bool:
        """Falsy only when the amount is zero, whatever the currency."""
        raise NotImplementedError


class Inventory:
    """A mutable mapping of item name -> quantity, behaving like a container.

        >>> inv = Inventory({"apple": 3})
        >>> len(inv), "apple" in inv, inv["apple"]
        (1, True, 3)

    Insertion order is preserved throughout.
    """

    _items: dict[str, int]  # your internal storage; a plain dict is the right call

    def __init__(self, items: Mapping[str, int] | None = None) -> None:
        """Copy `items` into internal state (never alias the caller's mapping).

        Raises:
            ValueError: if any starting quantity is negative.

        Quantities of 0 passed to the constructor are stored as-is; only
        __setitem__ treats 0 as a removal (see below).
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """>>> repr(Inventory({"apple": 3}))
        "Inventory({'apple': 3})"
        """
        raise NotImplementedError

    def __len__(self) -> int:
        """Number of DISTINCT items, not total quantity."""
        raise NotImplementedError

    def __getitem__(self, name: str) -> int:
        """Quantity for `name`.

        Raises:
            KeyError: if the item is not present.
        """
        raise NotImplementedError

    def __setitem__(self, name: str, quantity: int) -> None:
        """Set a quantity.

        Setting 0 REMOVES the item entirely (so len() drops). Setting 0 for an
        item that isn't present is a no-op, not an error.

        Raises:
            ValueError: if quantity is negative.
        """
        raise NotImplementedError

    def __delitem__(self, name: str) -> None:
        """Remove an item.

        Raises:
            KeyError: if the item is not present.
        """
        raise NotImplementedError

    def __contains__(self, name: object) -> bool:
        """Membership tests item NAMES, like a dict."""
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        """Iterate item names in insertion order.

        Must return a FRESH iterator each call, so the Inventory stays
        re-iterable. (Do not return self.)
        """
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Equal when the same items map to the same quantities.

        Order does NOT affect equality. Return NotImplemented for non-Inventory.
        """
        raise NotImplementedError

    def total(self) -> int:
        """Sum of all quantities. A plain method — no dunder needed."""
        raise NotImplementedError
