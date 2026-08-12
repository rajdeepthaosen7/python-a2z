"""Exercise 01 — sequences, dicts, comprehensions, sorting.

Implement every function. The docstring is the spec — treat it as a ticket.
Do NOT open the test file first.

Run:  uv run pytest modules/m01_language_core/tests/test_ex01_collections.py -x -q

Constraints (this is where the learning is — a correct-but-Java solution is a fail):
  * No `for i in range(len(...))`.
  * No manual `if key not in d` before inserting — use dict/collections idioms.
  * Every function keeps its type annotations.
  * Nothing longer than 8 lines of body.
"""

from collections.abc import Iterable, Mapping, Sequence


def unique_preserving_order(items: Iterable[str]) -> list[str]:
    """Return items with duplicates removed, keeping first-seen order.

    >>> unique_preserving_order(["b", "a", "b", "c", "a"])
    ['b', 'a', 'c']
    >>> unique_preserving_order([])
    []

    Hint: dict keys are an insertion-ordered set. One line is possible.
    """
    return list(dict.fromkeys(items))


def group_by_length(words: Iterable[str]) -> dict[int, list[str]]:
    """Group words by their length, preserving input order within each group.

    Empty strings are ignored.

    >>> group_by_length(["hi", "bye", "yo", "hello"])
    {2: ['hi', 'yo'], 3: ['bye'], 5: ['hello']}
    """
    raise NotImplementedError


def invert_index(mapping: Mapping[str, str]) -> dict[str, list[str]]:
    """Invert a mapping so each value maps to the sorted list of its keys.

    >>> invert_index({"a": "x", "b": "y", "c": "x"})
    {'x': ['a', 'c'], 'y': ['b']}

    Key order in the result follows first appearance of each value in `mapping`.
    """
    raise NotImplementedError


def top_n(counts: Mapping[str, int], n: int) -> list[tuple[str, int]]:
    """Return the n highest-count (key, count) pairs.

    Sort by count descending, then by key ascending (a stable, deterministic
    tie-break — never rely on dict order for output).

    >>> top_n({"a": 3, "b": 5, "c": 3}, 2)
    [('b', 5), ('a', 3)]
    >>> top_n({"a": 1}, 10)
    [('a', 1)]

    Raises:
        ValueError: if n is negative.
    """
    raise NotImplementedError


def chunked(items: Sequence[int], size: int) -> list[list[int]]:
    """Split items into consecutive chunks of at most `size` elements.

    The final chunk may be shorter. An empty input gives an empty list.

    >>> chunked([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]

    Raises:
        ValueError: if size < 1.

    Hint: slicing plus range(0, len(items), size). This is the one legitimate
    use of range with a step — you're computing offsets, not indexing elements.
    """
    raise NotImplementedError


def flatten_once(nested: Iterable[Iterable[int]]) -> list[int]:
    """Flatten one level of nesting.

    >>> flatten_once([[1, 2], [3], [], [4, 5]])
    [1, 2, 3, 4, 5]

    Hint: a nested comprehension reads outer-to-inner.
    """
    raise NotImplementedError


def merge_configs(base: Mapping[str, object], override: Mapping[str, object]) -> dict[str, object]:
    """Return a NEW dict with override's entries winning over base's.

    Neither input may be mutated.

    >>> merge_configs({"host": "localhost", "port": 5432}, {"port": 6543})
    {'host': 'localhost', 'port': 6543}
    """
    raise NotImplementedError


def rotate(items: Sequence[int], n: int) -> list[int]:
    """Rotate items left by n positions, wrapping around.

    Negative n rotates right. n may exceed len(items). Empty input gives [].

    >>> rotate([1, 2, 3, 4, 5], 2)
    [3, 4, 5, 1, 2]
    >>> rotate([1, 2, 3, 4, 5], -1)
    [5, 1, 2, 3, 4]
    >>> rotate([1, 2, 3], 7)
    [2, 3, 1]

    Hint: modulo plus two slices. No loop needed.
    """
    raise NotImplementedError


def running_totals(values: Iterable[int]) -> list[int]:
    """Return the cumulative sums of values.

    >>> running_totals([1, 2, 3, 4])
    [1, 3, 6, 10]
    >>> running_totals([])
    []

    Hint: itertools.accumulate exists. Use it, then look up three more
    itertools functions you didn't know about.
    """
    raise NotImplementedError


def pairwise_diffs(values: Sequence[int]) -> list[int]:
    """Return the difference between each consecutive pair of values.

    >>> pairwise_diffs([1, 4, 9, 16])
    [3, 5, 7]
    >>> pairwise_diffs([5])
    []

    Hint: zip(values, values[1:]) is the classic sliding-window idiom. Write
    that first, then run ruff and let it tell you about the modern alternative.
    """
    raise NotImplementedError
