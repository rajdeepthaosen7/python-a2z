"""Exercise 01 — functions as values, closures, memoization.

Run:  uv run pytest modules/m02_functions/tests/test_ex01_higher_order.py -x -q

Constraints:
  * `once`, `count_calls` and `memoize` are decorators and MUST use
    `functools.wraps`. A test checks `__name__` and `__doc__` survive.
  * No `global`. Use closures and `nonlocal`.
  * Keep the annotations.
"""

from collections.abc import Callable, Iterable
from typing import Any, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compose single-argument functions right-to-left (mathematical order).

    compose(f, g, h)(x) == f(g(h(x)))

    >>> compose(str, abs)(-5)
    '5'
    >>> compose()(42)          # no functions == identity
    42
    """
    raise NotImplementedError


def pipe(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    """Thread a value left-to-right through functions.

    pipe(x, f, g) == g(f(x))

    >>> pipe(-5, abs, str)
    '5'
    >>> pipe(42)
    42

    Note this is the opposite order to `compose`. Both exist in real codebases,
    which is exactly why you should name yours unambiguously.
    """
    raise NotImplementedError


def apply_n_times(fn: Callable[[T], T], n: int, value: T) -> T:
    """Apply fn to value n times.

    >>> apply_n_times(lambda x: x * 2, 3, 1)
    8
    >>> apply_n_times(lambda x: x * 2, 0, 1)
    1

    Raises:
        ValueError: if n is negative.
    """
    raise NotImplementedError


def make_counter(start: int = 0) -> Callable[[], int]:
    """Return a function that yields start, start+1, start+2, ... on each call.

    Each counter has independent state.

    >>> c = make_counter()
    >>> c(), c(), c()
    (0, 1, 2)
    >>> d = make_counter(10)
    >>> d(), c()
    (10, 3)

    This is the `nonlocal` exercise. No classes, no globals, no attributes.
    """
    raise NotImplementedError


def once(fn: Callable[..., T]) -> Callable[..., T]:
    """Decorator: call the wrapped function at most once, then replay its result.

    Later calls return the cached result and IGNORE their arguments — they do
    not re-invoke fn. Expose a boolean attribute `called` on the wrapper,
    False before the first call and True after.

    Real use: one-time initialization that might be triggered from several
    places (the lazy-singleton problem, minus the double-checked locking).
    """
    raise NotImplementedError


def count_calls(fn: Callable[..., T]) -> Callable[..., T]:
    """Decorator: add a `call_count` attribute to the wrapper.

    Starts at 0, increments on every invocation — including invocations where
    fn raises. (Think about where the increment has to go.)
    """
    raise NotImplementedError


def memoize(fn: Callable[..., T]) -> Callable[..., T]:
    """Decorator: cache results keyed by the positional argument tuple.

    Assume all arguments are positional and hashable — no kwargs.

    Expose on the wrapper:
        hits         int, incremented on a cache hit
        misses       int, incremented on a cache miss
        cache_clear  callable that empties the cache and zeroes both counters

    You are hand-building `functools.cache`. Do it once by hand so you know
    what it costs, then use the stdlib one forever after.
    """
    raise NotImplementedError


def group_by(items: Iterable[T], key: Callable[[T], K]) -> dict[K, list[T]]:
    """Group items by a key function, preserving order.

    Result keys appear in first-seen order; items keep their input order
    within each group.

    >>> group_by(["apple", "avocado", "beet"], key=lambda s: s[0])
    {'a': ['apple', 'avocado'], 'b': ['beet']}

    Note: `itertools.groupby` does NOT do this — it only groups *consecutive*
    equal keys, and requires pre-sorted input. This is the function people
    reach for groupby expecting.
    """
    raise NotImplementedError


def partition(items: Iterable[T], predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
    """Split items into (matching, non_matching), preserving order.

    >>> partition([1, 2, 3, 4], lambda n: n % 2 == 0)
    ([2, 4], [1, 3])

    Do it in ONE pass. Two comprehensions is two evaluations of the predicate.
    """
    raise NotImplementedError


def flat_map(items: Iterable[T], fn: Callable[[T], Iterable[K]]) -> list[K]:
    """Apply fn to each item and concatenate the resulting iterables.

    >>> flat_map(["a b", "c"], str.split)
    ['a', 'b', 'c']
    >>> flat_map([], str.split)
    []
    """
    raise NotImplementedError
