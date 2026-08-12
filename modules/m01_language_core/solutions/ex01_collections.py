from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from itertools import accumulate, pairwise


def unique_preserving_order(items: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(items))


def group_by_length(words: Iterable[str]) -> dict[int, list[str]]:
    groups: defaultdict[int, list[str]] = defaultdict(list)
    for word in words:
        if word:
            groups[len(word)].append(word)
    return dict(groups)


def invert_index(mapping: Mapping[str, str]) -> dict[str, list[str]]:
    out: defaultdict[str, list[str]] = defaultdict(list)
    for key, value in mapping.items():
        out[value].append(key)
    return {value: sorted(keys) for value, keys in out.items()}


def top_n(counts: Mapping[str, int], n: int) -> list[tuple[str, int]]:
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def chunked(items: Sequence[int], size: int) -> list[list[int]]:
    if size < 1:
        raise ValueError(f"size must be >= 1, got {size}")
    return [list(items[i : i + size]) for i in range(0, len(items), size)]


def flatten_once(nested: Iterable[Iterable[int]]) -> list[int]:
    return [item for inner in nested for item in inner]


def merge_configs(base: Mapping[str, object], override: Mapping[str, object]) -> dict[str, object]:
    return {**base, **override}


def rotate(items: Sequence[int], n: int) -> list[int]:
    if not items:
        return []
    k = n % len(items)
    return [*items[k:], *items[:k]]


def running_totals(values: Iterable[int]) -> list[int]:
    return list(accumulate(values))


def pairwise_diffs(values: Sequence[int]) -> list[int]:
    # zip(values, values[1:]) is the classic idiom and works everywhere, but it
    # slices a whole extra list. itertools.pairwise (3.10+) is lazy and is what
    # ruff's RUF007 will push you towards.
    return [b - a for a, b in pairwise(values)]
