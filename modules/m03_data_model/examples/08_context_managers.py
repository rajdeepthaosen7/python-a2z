"""Context managers and properties — try-with-resources, and getters you don't write.

Run me:  uv run python modules/m03_data_model/examples/08_context_managers.py
"""

import contextlib
from collections.abc import Iterator
from types import TracebackType
from typing import Literal


class Timer:
    """The class form: __enter__ / __exit__."""

    def __init__(self, label: str, clock: Iterator[float]) -> None:
        self.label = label
        self.clock = clock  # injected so this example is deterministic
        self.elapsed = 0.0

    def __enter__(self) -> "Timer":
        self.start = next(self.clock)
        print(f"     [{self.label}] enter")
        return self  # <- this is what `as t` binds

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        # Note the return type. mypy rejects a plain `-> bool` on an __exit__ that
        # always returns False, because `bool` tells callers it MIGHT suppress.
        # Literal[False] (or None) says "this never swallows your exception".
        self.elapsed = next(self.clock) - self.start
        status = "ok" if exc_type is None else f"failed with {exc_type.__name__}"
        print(f"     [{self.label}] exit ({status})")
        return False


class Swallower:
    """Returning True from __exit__ suppresses the exception. Almost always wrong."""

    def __enter__(self) -> "Swallower":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return True  # eats everything, silently


@contextlib.contextmanager
def transaction(log: list[str]) -> Iterator[list[str]]:
    """The lighter form. Exactly one yield, always inside try/finally."""
    log.append("BEGIN")
    try:
        yield log  # everything before = __enter__, after = __exit__
    except Exception:
        log.append("ROLLBACK")
        raise  # re-raise: the caller still needs to know
    else:
        log.append("COMMIT")
    finally:
        log.append("CLOSE")  # runs on every path


class Corpus:
    """Properties: computed attributes, no getters."""

    def __init__(self, name: str, body: str = "") -> None:
        self.name = name  # plain public attribute — start here
        self._body = body

    @property
    def word_count(self) -> int:
        # Callers write `corpus.word_count` with no parentheses. You can add
        # computation later without changing a single call site — which is why
        # writing getters up front is unnecessary in Python.
        return len(self._body.split())

    @property
    def body(self) -> str:
        return self._body

    @body.setter
    def body(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"body must be str, got {type(value).__name__}")
        self._body = value


def main() -> None:
    clock = iter([0.0, 1.5, 10.0, 12.25, 100.0, 100.5])

    # ---- 1. The class form -------------------------------------------------
    with Timer("load", clock) as timer:
        print("     doing work")
    print("1) elapsed:", timer.elapsed)

    # ---- 2. __exit__ runs even when the body raises -----------------------
    try:
        with Timer("risky", clock) as t2:
            raise ValueError("boom")
    except ValueError as exc:
        print("2) exception escaped, as it should:", exc, "| elapsed:", t2.elapsed)

    # ---- 3. Returning True swallows it — see how silent this is -----------
    with Swallower():
        raise RuntimeError("you will never hear about this")
    print("3) execution continues, error vanished. Do not do this.")

    # ---- 4. @contextmanager, happy path and failure path ------------------
    log: list[str] = []
    with transaction(log) as active:
        active.append("INSERT")
    print("4)", log)

    log2: list[str] = []
    try:
        with transaction(log2):
            log2.append("INSERT")
            raise ValueError("constraint violated")
    except ValueError:
        pass
    print("5)", log2)
    # That is @Transactional — except you can see exactly where it begins and ends.

    # ---- 5. contextlib helpers you'll actually use ------------------------
    config: dict[str, str] = {}
    with contextlib.suppress(KeyError):
        config["missing"]
    print("6) suppressed deliberately, and a reader can see it")

    with contextlib.ExitStack() as stack:
        # For a variable number of resources — all closed in reverse order.
        timers = [stack.enter_context(Timer(f"t{i}", iter([0.0, float(i)]))) for i in range(2)]
    print("7)", [t.elapsed for t in timers])

    # ---- 6. Properties ------------------------------------------------------
    corpus = Corpus("docs", "one two three")
    print("8)", corpus.word_count)  # no parentheses — looks like an attribute
    corpus.body = "one two three four"
    print("9)", corpus.word_count)  # recomputed

    try:
        corpus.body = 42  # type: ignore[assignment]
    except TypeError as exc:
        print("10)", exc)

    print("11)", type(Corpus.word_count).__name__)  # 'property' — a descriptor
    # A property is just an object implementing __get__/__set__ on the CLASS.
    # That mechanism is called the descriptor protocol, and it is also how
    # methods, classmethod, staticmethod, and ORM columns all work.

    # ---- 7. Guidance --------------------------------------------------------
    print("12) Start with a public attribute. Promote to @property when you")
    print("    need computation or validation — it is a non-breaking change,")
    print("    which is exactly why Java-style getters are unnecessary here.")


if __name__ == "__main__":
    main()
