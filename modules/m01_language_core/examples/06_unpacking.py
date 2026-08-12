"""Unpacking, multiple returns, and structural pattern matching.

Run me:  uv run python modules/m01_language_core/examples/06_unpacking.py
"""

from typing import Any


def main() -> None:
    # ---- 1. Basic and starred unpacking ---------------------------------
    a, b = 1, 2
    a, b = b, a  # swap without a temp
    print("1)", a, b)

    first, *rest = [1, 2, 3, 4]
    *init, last = [1, 2, 3, 4]
    head, *middle, tail = [1, 2, 3, 4, 5]
    print("2)", first, rest, init, last)
    print("2b)", head, middle, tail)

    # Nested, and the throwaway `_` convention
    (name, _), city = ("Ada", 1815), "London"
    print("3)", name, city)

    # Star-unpacking always yields a list, even from a tuple/str
    x, *y = "hello"  # type: ignore[str-unpack]
    print("4)", x, y)

    # ---- 2. Multiple return values are just tuples ----------------------
    def split_host(addr: str) -> tuple[str, int]:
        host, _, port = addr.rpartition(":")
        return host, int(port)

    host, port = split_host("db.internal:5432")
    print("5)", host, port)
    # No Pair class, no out-params, no wrapper record for two values.

    # ---- 3. Spreading into calls ----------------------------------------
    def connect(host: str, port: int, *, timeout: float = 5.0) -> str:
        return f"{host}:{port} t={timeout}"

    args = ("localhost", 5432)
    kwargs: dict[str, Any] = {"timeout": 1.5}
    print("6)", connect(*args, **kwargs))

    merged_list = [*[1, 2], *[3, 4]]
    merged_dict = {**{"a": 1}, **{"b": 2}}
    print("7)", merged_list, merged_dict)

    # ---- 4. Unpacking in loops ------------------------------------------
    pairs = [("a", 1), ("b", 2)]
    for key, value in pairs:
        print(f"8) {key}={value}")

    records = [("ada", ("eng", 120)), ("bob", ("ops", 90))]
    for who, (dept, salary) in records:  # nested unpack in the for target
        print(f"9) {who} {dept} {salary}")

    # ---- 5. match/case: switch that destructures ------------------------
    def describe(event: Any) -> str:
        match event:
            case {"type": "click", "x": int(x), "y": int(y)}:
                return f"click at {x},{y}"  # matches AND type-checks AND binds
            case {"type": "key", "code": code} if code < 32:
                return f"control key {code}"
            case {"type": "key", "code": code}:
                return f"key {code}"
            case [single]:
                return f"batch of one: {single}"
            case [first, *others]:
                return f"batch of {1 + len(others)} starting {first}"
            case str() as text:
                return f"raw text {text!r}"
            case _:
                raise ValueError(f"unhandled event: {event!r}")

    for ev in [
        {"type": "click", "x": 3, "y": 9},
        {"type": "key", "code": 13},
        {"type": "key", "code": 65},
        [42],
        [1, 2, 3],
        "hello",
    ]:
        print("10)", describe(ev))

    try:
        describe(3.14)
    except ValueError as exc:
        print("11)", exc)

    # No fallthrough, no break needed. `case _` is `default`.
    # `case Point(x=0, y=0)` also destructures your own classes (Module 03).


if __name__ == "__main__":
    main()
