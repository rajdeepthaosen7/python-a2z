"""Functions are objects. That single fact replaces several design patterns.

Run me:  uv run python modules/m02_functions/examples/01_first_class_functions.py
"""

from collections.abc import Callable
from operator import attrgetter, itemgetter

Formatter = Callable[[dict[str, object]], str]


def to_json(data: dict[str, object]) -> str:
    import json

    return json.dumps(data, sort_keys=True)


def to_csv(data: dict[str, object]) -> str:
    keys = sorted(data)
    return ",".join(keys) + "\n" + ",".join(str(data[k]) for k in keys)


def to_table(data: dict[str, object]) -> str:
    width = max((len(k) for k in data), default=0)
    return "\n".join(f"{k:<{width}} | {v}" for k, v in sorted(data.items()))


# The dispatch table: this IS the Strategy pattern. No interface, no classes,
# no component scanning. The functions are the implementations.
FORMATTERS: dict[str, Formatter] = {"json": to_json, "csv": to_csv, "table": to_table}


def render(data: dict[str, object], fmt: str) -> str:
    try:
        return FORMATTERS[fmt](data)
    except KeyError:
        # `from None` suppresses the KeyError chain — the caller doesn't care
        # that a dict lookup failed, only that the format was invalid.
        raise ValueError(f"unknown format {fmt!r}, expected one of {sorted(FORMATTERS)}") from None


def main() -> None:
    row: dict[str, object] = {"id": 7, "name": "ada", "dept": "eng"}

    # ---- 1. Functions have inspectable attributes -------------------------
    print("1)", to_json.__name__, to_json.__module__)
    print("2)", render.__doc__, render.__annotations__)

    # You can even attach your own attributes (decorators rely on this):
    to_json.content_type = "application/json"  # type: ignore[attr-defined]
    print("3)", to_json.content_type)  # type: ignore[attr-defined]

    # ---- 2. Bind, pass, and return them ---------------------------------
    alias = to_json  # alias, not a copy
    print("4)", alias is to_json, alias(row))

    for fmt in FORMATTERS:
        print(f"5) --- {fmt} ---\n{render(row, fmt)}")

    try:
        render(row, "xml")
    except ValueError as exc:
        print("6)", exc)

    # ---- 3. Higher-order functions --------------------------------------
    def call_twice(fn: Callable[[int], int], value: int) -> int:
        return fn(fn(value))

    print("7)", call_twice(lambda x: x * 3, 2))

    def make_adder(n: int) -> Callable[[int], int]:
        def add(x: int) -> int:
            return x + n  # closes over n

        return add

    add10 = make_adder(10)
    print("8)", add10(5), make_adder(100)(5))

    # ---- 4. Built-in higher-order functions -----------------------------
    words = ["delta", "alpha", "charlie", "bravo"]
    print("9)", sorted(words, key=len))
    print("10)", sorted(words, key=lambda w: (len(w), w)))
    print("11)", max(words, key=len), min(words, key=len))

    # map/filter exist but comprehensions are preferred — they read better
    # and don't need list() to materialize.
    print("12)", list(map(str.upper, words)), [w.upper() for w in words])

    # ---- 5. operator.itemgetter / attrgetter ----------------------------
    rows = [("ada", "eng", 120), ("bob", "ops", 90), ("cy", "eng", 150)]
    print("13)", sorted(rows, key=itemgetter(2), reverse=True))
    print("14)", sorted(rows, key=itemgetter(1, 0)))  # by dept, then name

    class Employee:
        def __init__(self, name: str, dept: str) -> None:
            self.name, self.dept = name, dept

        def __repr__(self) -> str:
            return f"Employee({self.name!r}, {self.dept!r})"

    staff = [Employee("cy", "eng"), Employee("ada", "eng"), Employee("bob", "ops")]
    print("15)", sorted(staff, key=attrgetter("dept", "name")))
    # attrgetter/itemgetter are C-implemented: faster than a lambda AND clearer.

    # ---- 6. Methods are functions bound to an instance -------------------
    bound = staff[0].__repr__
    unbound = Employee.__repr__
    print("16)", bound(), unbound(staff[1]))
    print("17)", str.upper("abc"), "abc".upper())  # same function, two spellings


if __name__ == "__main__":
    main()
