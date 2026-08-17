"""Exercise 03 — generators, laziness, a hand-written iterator, context managers.

Several tests assert LAZINESS, not just values: they feed in an infinite or
instrumented source and check that your function consumed only what it needed.
A correct-looking eager implementation that builds a list will fail them. That
is the point of the exercise — Athena Stage 3 streams a corpus that does not
fit in memory.

Run:  uv run pytest modules/m03_data_model/tests/test_ex03_iterators.py -x -q

Constraints:
  * Every function below whose return type is `Iterator[...]` must be a
    GENERATOR (contain `yield`). Returning a list will fail the laziness tests.
  * No `list(...)` over the whole input in any of them.
"""

from collections.abc import Callable, Iterable, Iterator
from contextlib import AbstractContextManager
from types import TracebackType
from typing import TypeVar

T = TypeVar("T")


def read_paragraphs(text: str) -> Iterator[str]:
    """Yield paragraphs, lazily.

    A paragraph is a run of consecutive non-blank lines. Paragraphs are
    separated by one or more blank lines. Each yielded paragraph has its lines
    joined with a single space, and is stripped. Blank runs yield nothing.

    >>> list(read_paragraphs("one\\ntwo\\n\\n\\nthree\\n"))
    ['one two', 'three']
    >>> list(read_paragraphs("   "))
    []

    Must be a generator: a huge document should not be materialized.
    """
    raise NotImplementedError


def chunked_stream(items: Iterable[T], size: int) -> Iterator[list[T]]:
    """Yield consecutive chunks of at most `size` items, lazily.

    The final chunk may be short. Contrast with Module 01's `chunked`, which
    took a Sequence and returned a list — this one accepts any Iterable
    (including an infinite generator) and yields as it goes.

    >>> list(chunked_stream([1, 2, 3, 4, 5], 2))
    [[1, 2], [3, 4], [5]]

    Raises:
        ValueError: if size < 1. It must raise on the FIRST next() call, which
            is what happens naturally if you validate inside the generator
            body. (A test checks that calling the function alone does not
            raise — that's generator semantics: no code runs until consumed.)
    """
    raise NotImplementedError


def running_max(values: Iterable[int]) -> Iterator[int]:
    """Yield the maximum seen so far, one value per input value.

    >>> list(running_max([3, 1, 4, 1, 5]))
    [3, 3, 4, 4, 5]
    >>> list(running_max([]))
    []
    """
    raise NotImplementedError


def take_until(values: Iterable[T], predicate: Callable[[T], bool]) -> Iterator[T]:
    """Yield values until `predicate` is true, EXCLUDING the matching value.

    Stops consuming the source immediately after the match — it must not read
    past it. (A test feeds an infinite source and checks exactly this.)

    >>> list(take_until([1, 2, 3, 4], lambda n: n > 2))
    [1, 2]
    """
    raise NotImplementedError


def unique_lazy(items: Iterable[T]) -> Iterator[T]:
    """Yield items with duplicates removed, first-seen order, lazily.

    The lazy counterpart to Module 01's `unique_preserving_order`. Works on an
    infinite source, so `dict.fromkeys` is NOT an option here.

    >>> list(unique_lazy(["b", "a", "b", "c"]))
    ['b', 'a', 'c']
    """
    raise NotImplementedError


class Countdown:
    """An ITERATOR (not merely an iterable) counting down to 1.

        >>> list(Countdown(3))
        [3, 2, 1]

    Because it is an iterator, it is single-use: a second iteration yields
    nothing. Implement `__iter__` returning self, and `__next__` raising
    StopIteration when exhausted.

    Raises:
        ValueError: from __init__, if start is negative. Zero is fine and
            yields nothing.
    """

    def __init__(self, start: int) -> None:
        raise NotImplementedError

    def __iter__(self) -> "Countdown":
        raise NotImplementedError

    def __next__(self) -> int:
        raise NotImplementedError


class Tracker:
    """A context manager recording entry, exit, and any exception type.

    On __enter__  : append "enter" to `events`, and return SELF.
    On __exit__   : append "exit" on success, or f"exit:{ExcName}" when the
                    body raised (use the exception CLASS name).
    Never suppresses — the exception must continue to propagate. Note the
    `-> None` return annotation: returning None is falsy, so nothing is
    suppressed, and mypy actively warns if you annotate `-> bool` on an
    __exit__ that always returns False.

        >>> events = []
        >>> with Tracker(events) as t:
        ...     pass
        >>> events
        ['enter', 'exit']

    Also expose a boolean attribute `failed`, False unless the body raised.
    """

    def __init__(self, events: list[str]) -> None:
        raise NotImplementedError

    def __enter__(self) -> "Tracker":
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError


def collecting(sink: list[str]) -> AbstractContextManager[list[str]]:
    """A @contextlib.contextmanager doing the same job as Tracker.

    Append "open" on entry, yield the sink itself, and append "close" on exit —
    on every path, including when the body raises. Do NOT suppress.

        >>> log = []
        >>> with collecting(log) as active:
        ...     active.append("work")
        >>> log
        ['open', 'work', 'close']

    Decorate this function with @contextlib.contextmanager and annotate it
    `-> Iterator[list[str]]` — the decorator turns that generator into a
    context manager, which is why the stub's declared return type here is the
    wider AbstractContextManager.
    """
    raise NotImplementedError
