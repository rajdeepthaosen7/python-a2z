"""__eq__ / __hash__: the same contract as Java, enforced more aggressively.

Run me:  uv run python modules/m03_data_model/examples/02_eq_and_hash.py
"""


class IdentityOnly:
    """No __eq__. Equality is identity — like Java's default Object.equals."""

    def __init__(self, value: int) -> None:
        self.value = value


class EqNoHash:
    """__eq__ without __hash__. Python makes this UNHASHABLE on purpose."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EqNoHash):
            return NotImplemented
        return self.value == other.value


class Point:
    """The correct pairing: __eq__ and __hash__ over the same fields."""

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented  # NOT raise TypeError
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))  # hash the SAME fields __eq__ compares


class MutablePoint(Point):
    """Hashable AND mutable. This combination is a bug factory — see part 5."""

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy


def main() -> None:
    # ---- 1. Default equality is identity ---------------------------------
    a, b = IdentityOnly(1), IdentityOnly(1)
    print("1)", a == b, a == a)  # False True
    print("2)", len({a, b}))  # 2 — hashable by identity

    # ---- 2. Defining __eq__ sets __hash__ to None ------------------------
    c, d = EqNoHash(1), EqNoHash(1)
    print("3)", c == d)  # True
    print("4) __hash__ is:", EqNoHash.__hash__)  # None
    try:
        {c}
    except TypeError as exc:
        print("5)", exc)
    # Python did this deliberately: you redefined equality, so the inherited
    # identity hash is now WRONG and would silently corrupt sets and dicts.

    # ---- 3. The correct pairing ------------------------------------------
    p, q = Point(1, 2), Point(1, 2)
    print("6)", p == q, hash(p) == hash(q))  # True True
    print("7)", len({p, q}))  # 1 — they collapse, as they should
    print("8)", {p: "origin-ish"}[q])  # q finds p's entry

    # ---- 4. NotImplemented, not TypeError --------------------------------
    print("9)", p == "not a point")  # False — Python fell back to identity
    print("10)", p != "not a point")  # True  — != derived from __eq__ for free
    # If __eq__ had raised TypeError, this comparison would crash instead of
    # answering, and `p in some_mixed_list` would explode.

    # ---- 5. Why mutable + hashable is a trap -----------------------------
    m = MutablePoint(0, 0)
    bucket = {m}
    print("11) before:", m in bucket, bucket)
    m.move(5, 5)  # the hash just changed underneath the set
    print("12) after: ", m in bucket, bucket)
    print("13) still there though:", any(x is m for x in bucket))
    # The object IS in the set, but lookup goes to the new hash bucket and
    # finds nothing. Identical to mutating a Java HashMap key. The fix:
    # make value objects immutable (frozen dataclass), or don't define
    # __hash__ on mutable classes and let Python keep them unhashable.

    # ---- 6. Equality does not imply ordering -----------------------------
    try:
        _ = Point(1, 2) < Point(3, 4)  # type: ignore[operator]
    except TypeError as exc:
        print("14)", exc)
    # __eq__ gives you == and !=. Ordering needs __lt__ etc. — see example 03.

    # ---- 7. What the builtins do -----------------------------------------
    print("15)", hash(42) == hash(42.0), 42 == 42.0)  # equal values hash equal
    print("16)", hash(("a", 1)))  # tuples hash their contents
    try:
        hash(["a", 1])  # lists are mutable -> deliberately unhashable
    except TypeError as exc:
        print("17)", exc)


if __name__ == "__main__":
    main()
