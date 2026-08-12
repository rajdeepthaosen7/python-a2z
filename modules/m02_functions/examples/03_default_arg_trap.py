"""The mutable-default-argument bug. Read this once; recognize it forever.

Run me:  uv run python modules/m02_functions/examples/03_default_arg_trap.py

There is no equivalent trap in Java, which is exactly why it catches Java devs.
"""

import time
from datetime import UTC, datetime
from typing import Any


def append_to_broken(item: str, target: list[str] = []) -> list[str]:  # noqa: B006
    """BUG: `[]` is created ONCE, when this def executes."""
    target.append(item)
    return target


def append_to_fixed(item: str, target: list[str] | None = None) -> list[str]:
    """Correct: None is the sentinel, and a fresh list is made per call."""
    if target is None:
        target = []
    target.append(item)
    return target


def stamp_broken(event: str, when: str = datetime.now(tz=UTC).isoformat()) -> str:
    """BUG: the timestamp is frozen at import time, not call time."""
    return f"{when} {event}"


def stamp_fixed(event: str, when: str | None = None) -> str:
    return f"{when or datetime.now(tz=UTC).isoformat()} {event}"


def cache_broken(key: str, store: dict[str, int] = {}) -> dict[str, int]:  # noqa: B006
    """Sometimes this bug is 'useful' — it's still a bug. Be explicit instead."""
    store[key] = store.get(key, 0) + 1
    return store


def main() -> None:
    # ---- 1. The shared list ---------------------------------------------
    print("1)", append_to_broken("a"))  # ['a']
    print("2)", append_to_broken("b"))  # ['a', 'b']  <- the same list!
    print("3)", append_to_broken("c"))  # ['a', 'b', 'c']

    print("4)", append_to_fixed("a"))  # ['a']
    print("5)", append_to_fixed("b"))  # ['b']  <- correct

    # You can see the shared object hanging off the function:
    print("6)", append_to_broken.__defaults__)

    # ---- 2. The frozen timestamp ----------------------------------------
    print("7)", stamp_broken("started"))
    time.sleep(0.05)
    print("8)", stamp_broken("finished"))  # identical timestamp
    print("9)", stamp_fixed("started"))
    time.sleep(0.05)
    print("10)", stamp_fixed("finished"))  # different, as intended

    # ---- 3. Explicit shared state, when you actually want it ------------
    print("11)", cache_broken("x"), cache_broken("x"), cache_broken("y"))
    # If you want a shared cache, SAY so — module-level, or functools.cache,
    # or an object attribute. Never as an accidental default argument.

    # ---- 4. Which defaults are safe -------------------------------------
    safe: list[Any] = [0, 0.0, "", None, (), frozenset(), True, 3.14]
    unsafe: list[Any] = [[], {}, set(), bytearray()]
    print("12) safe (immutable):", safe)
    print("13) unsafe (mutable):", unsafe)

    # Rule: if the default is mutable, or is the RESULT of a call, use None
    # as a sentinel and construct it inside the body.
    #
    # ruff catches both cases:
    #   B006  mutable-argument-default
    #   B008  function-call-in-default-argument
    #
    # Prove it:  uv run ruff check --select B006,B008 modules/m02_functions
    # The two trailing "noqa" comments on the broken functions above are how you
    # silence a rule when you're demonstrating a bug on purpose. Never in real code.


if __name__ == "__main__":
    main()
