"""Grader for ex01_higher_order."""

import pytest

from modules.m02_functions.exercises.ex01_higher_order import (
    apply_n_times,
    compose,
    count_calls,
    flat_map,
    group_by,
    make_counter,
    memoize,
    once,
    partition,
    pipe,
)


def double(x: int) -> int:
    return x * 2


def increment(x: int) -> int:
    return x + 1


class TestCompose:
    def test_right_to_left(self) -> None:
        # double(increment(3)) == 8, NOT increment(double(3)) == 7
        assert compose(double, increment)(3) == 8

    def test_three_functions(self) -> None:
        assert compose(str, double, increment)(4) == "10"

    def test_single_function(self) -> None:
        assert compose(double)(5) == 10

    def test_no_functions_is_identity(self) -> None:
        assert compose()(42) == 42

    def test_returns_a_reusable_callable(self) -> None:
        f = compose(double, increment)
        assert [f(1), f(2)] == [4, 6]


class TestPipe:
    def test_left_to_right(self) -> None:
        assert pipe(3, double, increment) == 7

    def test_no_functions_returns_value(self) -> None:
        assert pipe(42) == 42

    def test_type_can_change_along_the_pipe(self) -> None:
        assert pipe(-5, abs, str, len) == 1


class TestApplyNTimes:
    def test_applies_repeatedly(self) -> None:
        assert apply_n_times(double, 3, 1) == 8

    def test_zero_returns_input(self) -> None:
        assert apply_n_times(double, 0, 7) == 7

    def test_negative_raises(self) -> None:
        with pytest.raises(ValueError):
            apply_n_times(double, -1, 1)


class TestMakeCounter:
    def test_starts_at_zero_and_increments(self) -> None:
        counter = make_counter()
        assert [counter(), counter(), counter()] == [0, 1, 2]

    def test_custom_start(self) -> None:
        counter = make_counter(10)
        assert [counter(), counter()] == [10, 11]

    def test_counters_are_independent(self) -> None:
        first, second = make_counter(), make_counter(100)
        first()
        first()
        assert second() == 100
        assert first() == 2

    def test_no_shared_module_state(self) -> None:
        assert make_counter()() == 0
        assert make_counter()() == 0


class TestOnce:
    def test_underlying_runs_only_once(self) -> None:
        calls = []

        @once
        def initialize(value: str) -> str:
            calls.append(value)
            return f"init:{value}"

        assert initialize("a") == "init:a"
        assert initialize("b") == "init:a"  # cached, args ignored
        assert initialize("c") == "init:a"
        assert calls == ["a"]

    def test_called_attribute(self) -> None:
        @once
        def work() -> int:
            return 1

        assert work.called is False
        work()
        assert work.called is True

    def test_preserves_metadata(self) -> None:
        @once
        def documented() -> None:
            """My docstring."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "My docstring."


class TestCountCalls:
    def test_counts(self) -> None:
        @count_calls
        def work(n: int) -> int:
            return n

        assert work.call_count == 0
        work(1)
        work(2)
        work(3)
        assert work.call_count == 3

    def test_counts_calls_that_raise(self) -> None:
        @count_calls
        def boom() -> None:
            raise RuntimeError("nope")

        for _ in range(2):
            with pytest.raises(RuntimeError):
                boom()
        assert boom.call_count == 2

    def test_preserves_metadata(self) -> None:
        @count_calls
        def documented() -> None:
            """Doc."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Doc."

    def test_separate_counters_per_decorated_function(self) -> None:
        @count_calls
        def a() -> None: ...

        @count_calls
        def b() -> None: ...

        a()
        assert a.call_count == 1
        assert b.call_count == 0


class TestMemoize:
    def test_caches_by_arguments(self) -> None:
        calls = []

        @memoize
        def square(n: int) -> int:
            calls.append(n)
            return n * n

        assert [square(2), square(3), square(2), square(3), square(2)] == [4, 9, 4, 9, 4]
        assert calls == [2, 3]

    def test_hit_and_miss_counters(self) -> None:
        @memoize
        def identity(n: int) -> int:
            return n

        identity(1)
        identity(1)
        identity(2)
        assert identity.misses == 2
        assert identity.hits == 1

    def test_cache_clear_resets_everything(self) -> None:
        calls = []

        @memoize
        def work(n: int) -> int:
            calls.append(n)
            return n

        work(1)
        work(1)
        work.cache_clear()
        assert work.hits == 0
        assert work.misses == 0
        work(1)
        assert calls == [1, 1]  # recomputed after the clear

    def test_distinct_argument_tuples(self) -> None:
        @memoize
        def add(a: int, b: int) -> int:
            return a + b

        assert [add(1, 2), add(2, 1), add(1, 2)] == [3, 3, 3]
        assert add.misses == 2

    def test_preserves_metadata(self) -> None:
        @memoize
        def documented() -> None:
            """Doc."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Doc."


class TestGroupBy:
    def test_groups_preserving_order(self) -> None:
        assert group_by(["apple", "avocado", "beet"], key=lambda s: s[0]) == {
            "a": ["apple", "avocado"],
            "b": ["beet"],
        }

    def test_result_key_order_is_first_seen(self) -> None:
        result = group_by([3, 1, 4, 1, 5], key=lambda n: n % 2)
        assert list(result) == [1, 0]

    def test_non_consecutive_keys_still_group(self) -> None:
        """The difference from itertools.groupby, which needs sorted input."""
        assert group_by("aba", key=str) == {"a": ["a", "a"], "b": ["b"]}

    def test_empty(self) -> None:
        assert group_by([], key=len) == {}


class TestPartition:
    def test_splits(self) -> None:
        assert partition([1, 2, 3, 4], lambda n: n % 2 == 0) == ([2, 4], [1, 3])

    def test_all_match(self) -> None:
        assert partition([2, 4], lambda n: n % 2 == 0) == ([2, 4], [])

    def test_none_match(self) -> None:
        assert partition([1, 3], lambda n: n % 2 == 0) == ([], [1, 3])

    def test_empty(self) -> None:
        assert partition([], lambda n: True) == ([], [])

    def test_predicate_evaluated_once_per_item(self) -> None:
        seen: list[int] = []

        def predicate(n: int) -> bool:
            seen.append(n)
            return n > 1

        partition([1, 2, 3], predicate)
        assert seen == [1, 2, 3]


class TestFlatMap:
    def test_concatenates(self) -> None:
        assert flat_map(["a b", "c"], str.split) == ["a", "b", "c"]

    def test_empty_results_disappear(self) -> None:
        assert flat_map(["a", "", "b"], str.split) == ["a", "b"]

    def test_empty_input(self) -> None:
        assert flat_map([], str.split) == []

    def test_works_with_generators(self) -> None:
        assert flat_map([2, 3], lambda n: range(n)) == [0, 1, 0, 1, 2]
