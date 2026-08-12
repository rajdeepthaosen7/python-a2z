"""Closures, `nonlocal`, and the late-binding trap.

Run me:  uv run python modules/m02_functions/examples/04_closures.py
"""

from collections.abc import Callable


def main() -> None:
    # ---- 1. Reading an enclosing variable needs no keyword ---------------
    def make_multiplier(factor: int) -> Callable[[int], int]:
        def multiply(x: int) -> int:
            return x * factor  # just reads `factor`

        return multiply

    triple = make_multiplier(3)
    print("1)", triple(5), make_multiplier(10)(5))

    # `factor` outlived make_multiplier. You can see the captured cell:
    print("2)", triple.__code__.co_freevars, [c.cell_contents for c in triple.__closure__ or ()])

    # ---- 2. REBINDING needs nonlocal -------------------------------------
    def make_counter_broken(start: int = 0) -> Callable[[], int]:
        count = start

        def next_value() -> int:
            # count += 1  ->  UnboundLocalError: assignment makes it a NEW local
            return count

        return next_value

    def make_counter(start: int = 0) -> Callable[[], int]:
        count = start

        def next_value() -> int:
            nonlocal count  # "assign to the ENCLOSING function's variable"
            current = count
            count += 1
            return current

        return next_value

    print("3)", make_counter_broken()(), make_counter_broken()())
    counter = make_counter()
    print("4)", counter(), counter(), counter())
    other = make_counter(100)
    print("5)", other(), counter())  # independent state per closure

    # Mutation needs no keyword, because it doesn't rebind the name:
    def make_recorder() -> tuple[Callable[[str], None], list[str]]:
        seen: list[str] = []

        def record(item: str) -> None:
            seen.append(item)  # mutates — no nonlocal needed

        return record, seen

    record, seen = make_recorder()
    record("a")
    record("b")
    print("6)", seen)

    # ---- 3. The late-binding trap ---------------------------------------
    # Closures capture the VARIABLE, not its value at creation time.
    broken: list[Callable[[], int]] = [lambda: i for i in range(3)]
    print("7)", [f() for f in broken])  # [2, 2, 2] — all see the final i

    # A default argument is evaluated at lambda-creation time, so it captures
    # the CURRENT value of i. (mypy cannot infer a defaulted lambda param.)
    fixed: list[Callable[[], int]] = [lambda i=i: i for i in range(3)]  # type: ignore[misc]
    print("8)", [f() for f in fixed])  # [0, 1, 2]

    from functools import partial

    def identity(value: int) -> int:
        return value

    fixed2 = [partial(identity, i) for i in range(3)]  # clearer intent
    print("9)", [f() for f in fixed2])

    # Java sidesteps this by requiring captured locals be effectively final.
    # Python lets you do it and you have to know. This bites in loops that
    # build callbacks, retry handlers, or async tasks.

    # ---- 4. Closure vs class: pick by amount of state --------------------
    def make_rate_tracker() -> tuple[Callable[[bool], None], Callable[[], float]]:
        total = errors = 0

        def record(is_error: bool) -> None:
            nonlocal total, errors
            total += 1
            errors += int(is_error)

        def rate() -> float:
            return errors / total if total else 0.0

        return record, rate

    record_call, error_rate = make_rate_tracker()
    for failed in (False, True, False, False):
        record_call(failed)
    print("10)", error_rate())

    # Two related functions over shared state is the point where a class
    # becomes clearer. Rule of thumb: one function + one value -> closure.
    # Several functions + several values -> class (Module 03).

    class RateTracker:
        def __init__(self) -> None:
            self.total = self.errors = 0

        def record(self, is_error: bool) -> None:
            self.total += 1
            self.errors += int(is_error)

        @property
        def error_rate(self) -> float:
            return self.errors / self.total if self.total else 0.0

    tracker = RateTracker()
    for failed in (False, True, False, False):
        tracker.record(failed)
    print("11)", tracker.error_rate)

    # ---- 5. `global` — almost always the wrong answer -------------------
    # nonlocal -> enclosing function scope.  global -> module scope.
    # If you're reaching for `global`, you want a class, a closure, or to pass
    # the value as an argument. Scope resolution order is LEGB:
    #   Local -> Enclosing -> Global -> Builtins
    print("12)", len.__module__)  # `len` is found in Builtins


if __name__ == "__main__":
    main()
