"""Reference solution — read only after your own version is green."""

import functools
from collections.abc import Iterator, Mapping


@functools.total_ordering
class Money:
    __slots__ = ("amount", "currency")

    amount: int
    currency: str

    def __init__(self, amount: int, currency: str = "USD") -> None:
        if len(currency) != 3 or not currency.isalpha():
            raise ValueError(f"currency must be 3 letters, got {currency!r}")
        self.amount = amount
        self.currency = currency.upper()

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.amount / 100:.2f} {self.currency}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def _same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise TypeError(f"cannot mix {self.currency} and {other.currency}")

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return self.amount < other.amount

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: object) -> "Money":
        # bool is a subclass of int, so exclude it explicitly.
        if not isinstance(factor, int) or isinstance(factor, bool):
            return NotImplemented
        return Money(self.amount * factor, self.currency)

    def __rmul__(self, factor: object) -> "Money":
        return self.__mul__(factor)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __abs__(self) -> "Money":
        return Money(abs(self.amount), self.currency)

    def __bool__(self) -> bool:
        return self.amount != 0


class Inventory:
    def __init__(self, items: Mapping[str, int] | None = None) -> None:
        source = items or {}
        for name, quantity in source.items():
            if quantity < 0:
                raise ValueError(f"quantity for {name!r} must be >= 0, got {quantity}")
        self._items: dict[str, int] = dict(source)  # copy, never alias

    def __repr__(self) -> str:
        return f"Inventory({self._items!r})"

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, name: str) -> int:
        return self._items[name]

    def __setitem__(self, name: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError(f"quantity must be >= 0, got {quantity}")
        if quantity == 0:
            self._items.pop(name, None)  # removal; missing is a no-op
        else:
            self._items[name] = quantity

    def __delitem__(self, name: str) -> None:
        del self._items[name]

    def __contains__(self, name: object) -> bool:
        return name in self._items

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)  # a FRESH iterator each call

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Inventory):
            return NotImplemented
        return self._items == other._items

    def total(self) -> int:
        return sum(self._items.values())
