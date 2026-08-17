"""Reference solution — read only after your own version is green."""

import contextlib
from collections.abc import Callable, Iterable, Iterator
from types import TracebackType
from typing import TypeVar

T = TypeVar("T")


def read_paragraphs(text: str) -> Iterator[str]:
    buffer: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line:
            buffer.append(line)
        elif buffer:
            yield " ".join(buffer)
            buffer.clear()
    if buffer:  # the final paragraph, with no trailing blank line
        yield " ".join(buffer)


def chunked_stream(items: Iterable[T], size: int) -> Iterator[list[T]]:
    # Validating inside the body means it raises on the first next(), not on
    # the call — that is generator semantics, and a test checks for it.
    if size < 1:
        raise ValueError(f"size must be >= 1, got {size}")
    chunk: list[T] = []
    for item in items:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []  # rebind, don't clear — the caller holds the old list
    if chunk:
        yield chunk


def running_max(values: Iterable[int]) -> Iterator[int]:
    highest: int | None = None
    for value in values:
        highest = value if highest is None else max(highest, value)
        yield highest


def take_until(values: Iterable[T], predicate: Callable[[T], bool]) -> Iterator[T]:
    for value in values:
        if predicate(value):
            return  # stops immediately; never pulls the next value
        yield value


def unique_lazy(items: Iterable[T]) -> Iterator[T]:
    seen: set[T] = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            yield item


class Countdown:
    def __init__(self, start: int) -> None:
        if start < 0:
            raise ValueError(f"start must be non-negative, got {start}")
        self.current = start

    def __iter__(self) -> "Countdown":
        return self  # an ITERATOR returns itself, so it has a single position

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1


class Tracker:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.failed = False

    def __enter__(self) -> "Tracker":
        self.events.append("enter")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self.events.append("exit")
        else:
            self.failed = True
            self.events.append(f"exit:{exc_type.__name__}")
        # Returning None (falsy) never suppresses. mypy actively warns against
        # annotating -> bool when you always return False.


@contextlib.contextmanager
def collecting(sink: list[str]) -> Iterator[list[str]]:
    sink.append("open")
    try:
        yield sink
    finally:
        sink.append("close")  # finally, so it runs on every path
