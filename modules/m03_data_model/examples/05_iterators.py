"""Iterable vs iterator — the distinction that causes real bugs.

Run me:  uv run python modules/m03_data_model/examples/05_iterators.py
"""

from collections.abc import Iterable, Iterator


class Countdown:
    """An ITERATOR: has __next__, and __iter__ returns self. Single use."""

    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self) -> "Countdown":
        return self  # returns ITSELF — so there is only ever one position

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration  # this is how `for` knows to stop
        self.current -= 1
        return self.current + 1


class Ring:
    """An ITERABLE: __iter__ returns a FRESH iterator each time. Reusable."""

    def __init__(self, items: list[str]) -> None:
        self.items = items

    def __iter__(self) -> Iterator[str]:
        return iter(self.items)  # a brand-new iterator per call


def main() -> None:
    # ---- 1. The protocol, by hand ----------------------------------------
    nums = [1, 2, 3]
    it = iter(nums)  # calls nums.__iter__()
    print("1)", next(it), next(it))  # calls it.__next__()
    print("2)", list(it))  # [3] — the first two are consumed
    print("3)", list(it))  # []  — exhausted forever
    print("4)", list(nums))  # [1, 2, 3] — the LIST is untouched

    try:
        next(it)
    except StopIteration:
        print("5) StopIteration — what `for` catches for you")

    print("6)", next(iter([]), "default"))  # next() takes a default

    # ---- 2. A list is iterable, not an iterator --------------------------
    print("7)", hasattr(nums, "__iter__"), hasattr(nums, "__next__"))
    print("8)", hasattr(it, "__iter__"), hasattr(it, "__next__"))
    print("9)", iter(nums) is iter(nums))  # False — fresh each time
    print("10)", iter(it) is it)  # True  — an iterator returns itself

    # ---- 3. Your own iterator is SINGLE USE ------------------------------
    counter = Countdown(3)
    print("11)", list(counter))  # [3, 2, 1]
    print("12)", list(counter))  # []  — spent. Surprising if you forget.

    # ---- 4. Your own iterable is REUSABLE --------------------------------
    ring = Ring(["a", "b", "c"])
    print("13)", list(ring), list(ring))  # both full — fresh iterator each time

    # ---- 5. The bug this causes, for real --------------------------------
    def summarize_broken(items: Iterable[int]) -> tuple[int, float]:
        total = sum(items)  # first pass consumes a generator...
        count = sum(1 for _ in items)  # ...so the second pass sees nothing
        return total, (total / count if count else 0.0)

    def summarize_fixed(items: Iterable[int]) -> tuple[int, float]:
        values = list(items)  # materialize ONCE at the boundary
        return sum(values), (sum(values) / len(values) if values else 0.0)

    print("14) list  :", summarize_broken([1, 2, 3]))  # works
    print("15) genexp:", summarize_broken(n for n in [1, 2, 3]))  # (6, 0.0) — WRONG
    print("16) fixed :", summarize_fixed(n for n in [1, 2, 3]))
    # Rule: if a function takes Iterable and needs two passes, list() it first.
    # If it only needs one pass, DON'T — you'd throw away the laziness.

    # ---- 6. Everything that "just works" once __iter__ exists ------------
    ring2 = Ring(["delta", "alpha", "charlie"])
    print("17)", sorted(ring2), max(ring2, key=len), "alpha" in ring2)
    print("18)", [s.upper() for s in ring2], dict.fromkeys(ring2))
    first, *rest = ring2
    print("19)", first, rest)
    print("20)", list(zip(ring2, Countdown(3), strict=False)))
    # None of that is code you wrote. That's the payoff of the protocol.

    # ---- 7. `in` falls back to __iter__ ----------------------------------
    # Ring has no __contains__, yet `in` worked above: Python walked __iter__
    # comparing each element. Define __contains__ when you can do better than
    # a linear scan (e.g. a set lookup underneath).

    # ---- 8. reversed() needs __reversed__ or __len__ + __getitem__ -------
    try:
        list(reversed(ring2))  # type: ignore[call-overload]
    except TypeError as exc:
        print("21)", exc)


if __name__ == "__main__":
    main()
