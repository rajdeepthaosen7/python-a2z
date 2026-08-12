"""Grader for ex01_collections. Read this only AFTER you've attempted the exercise.

Note the pytest idioms on display here — you'll write them yourself in Module 06:
  * plain `assert` (pytest rewrites it to produce a rich diff on failure)
  * `@pytest.mark.parametrize` — JUnit's @ParameterizedTest, but readable
  * `pytest.raises` as a context manager — JUnit's assertThrows
"""

import pytest

from modules.m01_language_core.exercises.ex01_collections import (
    chunked,
    flatten_once,
    group_by_length,
    invert_index,
    merge_configs,
    pairwise_diffs,
    rotate,
    running_totals,
    top_n,
    unique_preserving_order,
)


class TestUniquePreservingOrder:
    def test_removes_duplicates_keeping_first_occurrence(self) -> None:
        assert unique_preserving_order(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]

    def test_empty(self) -> None:
        assert unique_preserving_order([]) == []

    def test_already_unique_is_unchanged(self) -> None:
        assert unique_preserving_order(["x", "y", "z"]) == ["x", "y", "z"]

    def test_accepts_any_iterable_not_just_list(self) -> None:
        assert unique_preserving_order(iter(["a", "a", "b"])) == ["a", "b"]


class TestGroupByLength:
    def test_groups_and_preserves_input_order_within_group(self) -> None:
        assert group_by_length(["hi", "bye", "yo", "hello"]) == {
            2: ["hi", "yo"],
            3: ["bye"],
            5: ["hello"],
        }

    def test_ignores_empty_strings(self) -> None:
        assert group_by_length(["", "a", ""]) == {1: ["a"]}

    def test_empty_input(self) -> None:
        assert group_by_length([]) == {}


class TestInvertIndex:
    def test_keys_are_sorted_per_value(self) -> None:
        assert invert_index({"a": "x", "b": "y", "c": "x"}) == {"x": ["a", "c"], "y": ["b"]}

    def test_result_key_order_follows_first_appearance(self) -> None:
        result = invert_index({"k1": "z", "k2": "a", "k3": "z"})
        assert list(result) == ["z", "a"]

    def test_empty(self) -> None:
        assert invert_index({}) == {}


class TestTopN:
    def test_sorts_by_count_desc_then_key_asc(self) -> None:
        assert top_n({"a": 3, "b": 5, "c": 3}, 2) == [("b", 5), ("a", 3)]

    def test_ties_broken_alphabetically(self) -> None:
        assert top_n({"z": 1, "a": 1, "m": 1}, 3) == [("a", 1), ("m", 1), ("z", 1)]

    def test_n_larger_than_input(self) -> None:
        assert top_n({"a": 1}, 10) == [("a", 1)]

    def test_n_zero(self) -> None:
        assert top_n({"a": 1}, 0) == []

    def test_negative_n_raises(self) -> None:
        with pytest.raises(ValueError):
            top_n({"a": 1}, -1)


class TestChunked:
    @pytest.mark.parametrize(
        ("items", "size", "expected"),
        [
            ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),
            ([1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
            ([1, 2, 3], 1, [[1], [2], [3]]),
            ([1, 2, 3], 10, [[1, 2, 3]]),
            ([], 3, []),
        ],
    )
    def test_chunking(self, items: list[int], size: int, expected: list[list[int]]) -> None:
        assert chunked(items, size) == expected

    @pytest.mark.parametrize("size", [0, -1])
    def test_invalid_size_raises(self, size: int) -> None:
        with pytest.raises(ValueError):
            chunked([1, 2, 3], size)


class TestFlattenOnce:
    def test_flattens_one_level(self) -> None:
        assert flatten_once([[1, 2], [3], [], [4, 5]]) == [1, 2, 3, 4, 5]

    def test_empty(self) -> None:
        assert flatten_once([]) == []

    def test_works_with_mixed_iterables(self) -> None:
        assert flatten_once([(1, 2), [3], range(4, 6)]) == [1, 2, 3, 4, 5]


class TestMergeConfigs:
    def test_override_wins(self) -> None:
        assert merge_configs({"host": "localhost", "port": 5432}, {"port": 6543}) == {
            "host": "localhost",
            "port": 6543,
        }

    def test_new_keys_are_added(self) -> None:
        assert merge_configs({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

    def test_inputs_are_not_mutated(self) -> None:
        base = {"a": 1}
        override = {"a": 2}
        result = merge_configs(base, override)
        assert base == {"a": 1}
        assert override == {"a": 2}
        assert result is not base and result is not override


class TestRotate:
    @pytest.mark.parametrize(
        ("items", "n", "expected"),
        [
            ([1, 2, 3, 4, 5], 2, [3, 4, 5, 1, 2]),
            ([1, 2, 3, 4, 5], 0, [1, 2, 3, 4, 5]),
            ([1, 2, 3, 4, 5], 5, [1, 2, 3, 4, 5]),
            ([1, 2, 3, 4, 5], -1, [5, 1, 2, 3, 4]),
            ([1, 2, 3], 7, [2, 3, 1]),
            ([1, 2, 3], -7, [3, 1, 2]),
            ([], 3, []),
            ([1], 100, [1]),
        ],
    )
    def test_rotation(self, items: list[int], n: int, expected: list[int]) -> None:
        assert rotate(items, n) == expected

    def test_does_not_mutate_input(self) -> None:
        items = [1, 2, 3]
        rotate(items, 1)
        assert items == [1, 2, 3]


class TestRunningTotals:
    def test_cumulative(self) -> None:
        assert running_totals([1, 2, 3, 4]) == [1, 3, 6, 10]

    def test_empty(self) -> None:
        assert running_totals([]) == []

    def test_negatives(self) -> None:
        assert running_totals([5, -2, -3]) == [5, 3, 0]


class TestPairwiseDiffs:
    def test_diffs(self) -> None:
        assert pairwise_diffs([1, 4, 9, 16]) == [3, 5, 7]

    def test_single_element(self) -> None:
        assert pairwise_diffs([5]) == []

    def test_empty(self) -> None:
        assert pairwise_diffs([]) == []

    def test_negative_diffs(self) -> None:
        assert pairwise_diffs([10, 4, 4]) == [-6, 0]
