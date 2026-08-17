"""Protocol vs ABC: structural typing, and the capability Java interfaces lack.

Run me:  uv run python modules/m03_data_model/examples/07_protocols_and_abcs.py
"""

import re
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


# ---- 1. Protocol: structural. Nothing inherits from it. -----------------
class Tokenizer(Protocol):
    """Anything with a matching `tokenize` IS a Tokenizer. No registration."""

    def tokenize(self, text: str) -> list[str]: ...


class WhitespaceTokenizer:
    """Note: does NOT inherit from Tokenizer. Doesn't need to."""

    def tokenize(self, text: str) -> list[str]:
        return text.split()


class RegexTokenizer:
    def __init__(self, pattern: str = r"[a-z0-9]+") -> None:
        self.pattern = pattern

    def tokenize(self, text: str) -> list[str]:
        return re.findall(self.pattern, text.lower())


class NotATokenizer:
    def split_it(self, text: str) -> list[str]:
        return list(text)


def index(text: str, tokenizer: Tokenizer) -> dict[str, int]:
    """mypy verifies the SHAPE of whatever you pass. No base class required."""
    counts: dict[str, int] = {}
    for token in tokenizer.tokenize(text):
        counts[token] = counts.get(token, 0) + 1
    return counts


# ---- 2. runtime_checkable, for isinstance() ------------------------------
@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...


class Connection:
    def close(self) -> None:
        print("     connection closed")


# ---- 3. ABC: nominal, with shared implementation ------------------------
class Store(ABC):
    """Use an ABC when subclasses genuinely SHARE code."""

    @abstractmethod
    def read(self, key: str) -> str: ...

    @abstractmethod
    def write(self, key: str, value: str) -> None: ...

    def copy(self, src: str, dst: str) -> None:
        # Shared implementation — the thing a Protocol cannot give you.
        self.write(dst, self.read(src))


class MemoryStore(Store):
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def read(self, key: str) -> str:
        return self.data[key]

    def write(self, key: str, value: str) -> None:
        self.data[key] = value


class BrokenStore(Store):
    def read(self, key: str) -> str:
        return "x"

    # forgot write() entirely


def main() -> None:
    text = "the cat the hat"

    # ---- 4. Duck typing, verified by mypy --------------------------------
    print("1)", index(text, WhitespaceTokenizer()))
    print("2)", index("The CAT, the HAT!", RegexTokenizer()))
    # Both satisfy Tokenizer without importing or inheriting it.

    # The real payoff: a class from a library you don't control, written years
    # before your protocol existed, satisfies it automatically. Java interfaces
    # cannot do this — you'd need an adapter for every third-party type.

    # ---- 5. What mypy rejects ---------------------------------------------
    # index(text, NotATokenizer())
    #   -> error: Argument 2 has incompatible type "NotATokenizer";
    #      expected "Tokenizer"
    # Caught at review time. At RUNTIME, plain Protocols are invisible:
    print("3)", isinstance(WhitespaceTokenizer(), object))
    try:
        isinstance(WhitespaceTokenizer(), Tokenizer)  # type: ignore[misc]
    except TypeError as exc:
        print("4)", exc)

    # ---- 6. runtime_checkable enables isinstance --------------------------
    print("5)", isinstance(Connection(), Closeable))  # True — has close()
    print("6)", isinstance(NotATokenizer(), Closeable))  # False
    # Caveat: it only checks that the NAMES exist, never the signatures.

    # ---- 7. ABC: enforced at instantiation --------------------------------
    store = MemoryStore()
    store.write("a", "hello")
    store.copy("a", "b")  # inherited implementation
    print("7)", store.data)

    try:
        BrokenStore()  # type: ignore[abstract]
    except TypeError as exc:
        print("8)", exc)
    # A hard runtime error the moment you construct it — Protocol gives you
    # a type-check-time error instead, and nothing at runtime.

    print("9)", isinstance(store, Store), Store.__abstractmethods__)

    # ---- 8. The stdlib ABCs you should know ------------------------------
    from collections.abc import Iterable, Mapping, Sequence, Sized

    print("10)", isinstance([1], Sequence), isinstance({1: 2}, Mapping))
    print("11)", isinstance("abc", Iterable), isinstance({1, 2}, Sized))
    print("12)", isinstance((1, 2), Sequence), isinstance({1, 2}, Sequence))
    # Annotate parameters with the WIDEST type you actually need:
    #   Iterable  - you only loop over it once
    #   Sequence  - you need indexing or len()
    #   Mapping   - you need key lookup but will not mutate
    # Taking `list[str]` when Iterable would do is the Python equivalent of
    # declaring `ArrayList` instead of `List` in a method signature.

    # ---- 9. Choosing --------------------------------------------------------
    print("13) Protocol : structural, third-party types work, no shared code")
    print("14) ABC      : nominal, shared implementation, runtime enforcement")
    print("15) Default to Protocol. Use ABC when subclasses share real code.")


if __name__ == "__main__":
    main()
