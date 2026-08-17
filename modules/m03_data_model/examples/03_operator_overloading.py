"""Operator overloading and ordering — the thing the JVM won't let you do.

Run me:  uv run python modules/m03_data_model/examples/03_operator_overloading.py
"""

import functools


class Money:
    """A currency amount in minor units (cents). Immutable by convention."""

    __slots__ = ("amount", "currency")  # no per-instance __dict__

    def __init__(self, amount: int, currency: str = "USD") -> None:
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self) -> str:
        return f"{self.amount / 100:.2f} {self.currency}"

    # --- equality ----------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    # --- arithmetic --------------------------------------------------------
    def _check(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise TypeError(f"cannot mix {self.currency} and {other.currency}")

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: object) -> "Money":
        if not isinstance(factor, int) or isinstance(factor, bool):
            return NotImplemented
        return Money(self.amount * factor, self.currency)

    # __rmul__ handles `3 * money`. Python tries int.__mul__(Money) first,
    # gets NotImplemented, then tries the REFLECTED operation on Money.
    __rmul__ = __mul__

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __abs__(self) -> "Money":
        return Money(abs(self.amount), self.currency)

    def __bool__(self) -> bool:
        return self.amount != 0


@functools.total_ordering
class Version:
    """total_ordering derives <=, >, >= from just __eq__ and __lt__."""

    def __init__(self, text: str) -> None:
        self.parts = tuple(int(p) for p in text.split("."))

    def __repr__(self) -> str:
        return f"Version({'.'.join(map(str, self.parts))!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts

    def __hash__(self) -> int:
        return hash(self.parts)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts < other.parts  # tuples compare element-wise


def main() -> None:
    ten = Money(1000)
    five = Money(500)

    # ---- 1. Arithmetic reads like arithmetic -----------------------------
    print("1)", ten + five, "|", ten - five, "|", repr(ten + five))
    print("2)", ten * 3, "|", 3 * ten)  # __rmul__ handles the second one
    print("3)", -ten, "|", abs(Money(-250)))
    print("4)", bool(Money(0)), bool(Money(1)))

    # ---- 2. NotImplemented in action -------------------------------------
    try:
        ten + 5  # int is not Money -> NotImplemented -> Python raises
    except TypeError as exc:
        print("5)", exc)
    # Note the error message names BOTH types. That's Python's, not ours —
    # a benefit of returning NotImplemented instead of raising our own.

    try:
        ten + Money(500, "EUR")  # our own domain rule, so we DO raise
    except TypeError as exc:
        print("6)", exc)

    # ---- 3. Ordering is separate from equality ---------------------------
    versions = [Version("1.10.0"), Version("1.2.0"), Version("2.0.0")]
    print("7)", sorted(versions))
    print("8)", Version("1.2.0") <= Version("1.10.0"))  # from total_ordering
    print("9)", max(versions), min(versions))
    # Note 1.10.0 > 1.2.0 — because we compare tuples of ints, not strings.
    print("10) string sort would be wrong:", sorted(["1.10.0", "1.2.0"]))

    # ---- 4. Operators you get for free once __eq__/__lt__ exist ----------
    print("11)", Version("1.0") != Version("2.0"), Version("2.0") > Version("1.0"))

    # ---- 5. __slots__ ----------------------------------------------------
    print("12)", Money.__slots__)
    try:
        ten.typo = 1  # type: ignore[attr-defined]
    except AttributeError as exc:
        print("13)", exc)
    # __slots__ removes the per-instance __dict__: less memory, faster access,
    # and typos become errors instead of silently creating a new attribute.
    # Cost: no dynamic attributes. Worth it for value objects you make millions of.

    # ---- 6. The full operator table (know it exists) ---------------------
    print("14) arithmetic:  __add__ __sub__ __mul__ __truediv__ __floordiv__ __mod__ __pow__")
    print("15) bitwise:     __and__ __or__ __xor__ __lshift__ __rshift__ __invert__")
    print("16) reflected:   __radd__ ... (right operand's turn)")
    print("17) in-place:    __iadd__ ... (for `x += y`; falls back to __add__)")
    print("18) comparison:  __lt__ __le__ __gt__ __ge__ __eq__ __ne__")
    # Overload only where the operator's MEANING is obvious. Money + Money is
    # obvious. `user + order` is not — write a method with a name.


if __name__ == "__main__":
    main()
