"""Reference solution — read only after your own version is green."""

import functools
from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import Any, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def composed(value: Any) -> Any:
        for fn in reversed(funcs):
            value = fn(value)
        return value

    return composed


def pipe(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    for fn in funcs:
        value = fn(value)
    return value


def apply_n_times(fn: Callable[[T], T], n: int, value: T) -> T:
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    for _ in range(n):
        value = fn(value)
    return value


def make_counter(start: int = 0) -> Callable[[], int]:
    count = start

    def next_value() -> int:
        nonlocal count
        current = count
        count += 1
        return current

    return next_value


def once(fn: Callable[..., T]) -> Callable[..., T]:
    result: Any = None

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        nonlocal result
        if not wrapper.called:  # type: ignore[attr-defined]
            result = fn(*args, **kwargs)
            wrapper.called = True  # type: ignore[attr-defined]
        return result  # type: ignore[no-any-return]

    wrapper.called = False  # type: ignore[attr-defined]
    return wrapper


def count_calls(fn: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Increment BEFORE the call, so failures are counted too.
        wrapper.call_count += 1  # type: ignore[attr-defined]
        return fn(*args, **kwargs)

    wrapper.call_count = 0  # type: ignore[attr-defined]
    return wrapper


def memoize(fn: Callable[..., T]) -> Callable[..., T]:
    cache: dict[tuple[Any, ...], T] = {}

    @functools.wraps(fn)
    def wrapper(*args: Any) -> T:
        if args in cache:
            wrapper.hits += 1  # type: ignore[attr-defined]
            return cache[args]
        wrapper.misses += 1  # type: ignore[attr-defined]
        cache[args] = fn(*args)
        return cache[args]

    def cache_clear() -> None:
        cache.clear()
        wrapper.hits = wrapper.misses = 0  # type: ignore[attr-defined]

    wrapper.hits = wrapper.misses = 0  # type: ignore[attr-defined]
    wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
    return wrapper


def group_by(items: Iterable[T], key: Callable[[T], K]) -> dict[K, list[T]]:
    groups: defaultdict[K, list[T]] = defaultdict(list)
    for item in items:
        groups[key(item)].append(item)
    return dict(groups)


def partition(items: Iterable[T], predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
    matching: list[T] = []
    rest: list[T] = []
    for item in items:
        (matching if predicate(item) else rest).append(item)
    return matching, rest


def flat_map(items: Iterable[T], fn: Callable[[T], Iterable[K]]) -> list[K]:
    return [result for item in items for result in fn(item)]
