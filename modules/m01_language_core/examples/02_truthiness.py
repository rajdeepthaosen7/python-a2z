"""Truthiness, `or` defaults, and the None-vs-falsy trap.

Run me:  uv run python modules/m01_language_core/examples/02_truthiness.py
"""

from typing import Any

FALSY: list[Any] = [False, None, 0, 0.0, 0j, "", [], {}, (), set(), range(0)]


def main() -> None:
    # ---- 1. What is falsy --------------------------------------------------
    print("1) all falsy:", all(not v for v in FALSY))

    # Anything else is truthy, including these surprises:
    for v in ["0", "False", [0], {0: 0}, -1, 0.1]:
        print(f"   {v!r:>10} -> {bool(v)}")

    # ---- 2. The idiom -----------------------------------------------------
    items: list[int] = []
    if not items:  # idiomatic
        print("2) empty")
    if len(items) == 0:  # correct, but reads as a Java accent
        print("   also empty")

    # ---- 3. `and` / `or` return OPERANDS, not booleans ---------------------
    print("3)", "" or "default")  # 'default'
    print("  ", "given" or "default")  # 'given'
    print("  ", 0 or 42)  # 42
    print("  ", "a" and "b")  # 'b'  -> last truthy
    print("  ", None and "b")  # type: ignore[unreachable]  # None -> short-circuits

    # This makes `x or default` a compact fallback... with a sharp edge:
    def apply_timeout_wrong(timeout: float | None) -> float:
        return timeout or 30.0  # BUG: timeout=0 (no wait) becomes 30

    def apply_timeout_right(timeout: float | None) -> float:
        return 30.0 if timeout is None else timeout

    print("4) wrong:", apply_timeout_wrong(0), " right:", apply_timeout_right(0))

    # ---- 4. Same trap with dict.get ---------------------------------------
    config = {"retries": 0, "name": ""}
    print("5)", config.get("retries") or 3)  # 3   <- wrong
    print("  ", config.get("retries", 3))  # 0   <- right
    # .get's default applies only when the KEY IS ABSENT, which is what you mean.

    # ---- 5. Comparison chaining and `in` ----------------------------------
    age = 25
    print("6)", 18 <= age < 65)  # chained, evaluated once
    print("  ", "py" in "python", 3 in [1, 2, 3], "k" in {"k": 1})

    # ---- 6. Making your own objects truthy --------------------------------
    class Basket:
        def __init__(self, items: list[str]) -> None:
            self.items = items

        def __len__(self) -> int:  # bool() falls back to len() == 0
            return len(self.items)

    print("7)", bool(Basket([])), bool(Basket(["apple"])))
    # Define __bool__ for explicit control; otherwise __len__ is used;
    # otherwise every object is truthy.


if __name__ == "__main__":
    main()
