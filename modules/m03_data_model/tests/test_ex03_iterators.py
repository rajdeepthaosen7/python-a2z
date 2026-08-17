"""Grader for ex03_iterators.

Several tests here check LAZINESS, not just return values. They use an
instrumented source that records what was consumed, or an infinite source that
would hang an eager implementation.
"""

import inspect
import itertools
from collections.abc import Iterator

import pytest

from modules.m03_data_model.exercises.ex03_iterators import (
    Countdown,
    Tracker,
    chunked_stream,
    collecting,
    read_paragraphs,
    running_max,
    take_until,
    unique_lazy,
)


def spy(values: list[int], seen: list[int]) -> Iterator[int]:
    """A source that records every value actually pulled from it."""
    for value in values:
        seen.append(value)
        yield value


def naturals() -> Iterator[int]:
    """Infinite. Any eager implementation will hang on this."""
    return itertools.count()


class TestAreGenerators:
    @pytest.mark.parametrize(
        "fn", [read_paragraphs, chunked_stream, running_max, take_until, unique_lazy]
    )
    def test_is_a_generator_function(self, fn: object) -> None:
        """Returning a list would pass some value tests but defeats the exercise."""
        assert inspect.isgeneratorfunction(fn)


class TestReadParagraphs:
    def test_splits_on_blank_lines(self) -> None:
        assert list(read_paragraphs("one\ntwo\n\n\nthree\n")) == ["one two", "three"]

    def test_single_paragraph(self) -> None:
        assert list(read_paragraphs("just one line")) == ["just one line"]

    def test_joins_lines_with_a_single_space(self) -> None:
        assert list(read_paragraphs("a\nb\nc")) == ["a b c"]

    @pytest.mark.parametrize("text", ["", "   ", "\n\n\n", "  \n \n  "])
    def test_no_paragraphs(self, text: str) -> None:
        assert list(read_paragraphs(text)) == []

    def test_strips_surrounding_whitespace(self) -> None:
        assert list(read_paragraphs("  one  \n  two  \n\n three ")) == ["one two", "three"]

    def test_trailing_blank_lines_do_not_add_an_empty_paragraph(self) -> None:
        assert list(read_paragraphs("one\n\n\n\n")) == ["one"]


class TestChunkedStream:
    def test_chunks(self) -> None:
        assert list(chunked_stream([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]

    def test_exact_multiple(self) -> None:
        assert list(chunked_stream([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]

    def test_size_larger_than_input(self) -> None:
        assert list(chunked_stream([1, 2], 10)) == [[1, 2]]

    def test_empty_input_yields_nothing(self) -> None:
        assert list(chunked_stream([], 3)) == []

    def test_calling_it_does_not_run_any_code(self) -> None:
        """Generator semantics: the body runs on the first next(), not on call."""
        chunked_stream([1, 2, 3], 0)  # must NOT raise here

    @pytest.mark.parametrize("size", [0, -1])
    def test_invalid_size_raises_on_consumption(self, size: int) -> None:
        with pytest.raises(ValueError):
            list(chunked_stream([1, 2, 3], size))

    def test_works_on_an_infinite_source(self) -> None:
        chunks = chunked_stream(naturals(), 3)
        assert [next(chunks), next(chunks)] == [[0, 1, 2], [3, 4, 5]]

    def test_consumes_only_what_it_yields(self) -> None:
        seen: list[int] = []
        chunks = chunked_stream(spy([1, 2, 3, 4, 5, 6], seen), 2)
        next(chunks)
        assert seen == [1, 2]


class TestRunningMax:
    def test_running_maximum(self) -> None:
        assert list(running_max([3, 1, 4, 1, 5])) == [3, 3, 4, 4, 5]

    def test_monotonic_input(self) -> None:
        assert list(running_max([1, 2, 3])) == [1, 2, 3]

    def test_descending_input(self) -> None:
        assert list(running_max([5, 4, 3])) == [5, 5, 5]

    def test_negatives(self) -> None:
        assert list(running_max([-5, -10, -1])) == [-5, -5, -1]

    def test_empty(self) -> None:
        assert list(running_max([])) == []

    def test_lazy_on_infinite_source(self) -> None:
        assert list(itertools.islice(running_max(naturals()), 4)) == [0, 1, 2, 3]


class TestTakeUntil:
    def test_excludes_the_matching_value(self) -> None:
        assert list(take_until([1, 2, 3, 4], lambda n: n > 2)) == [1, 2]

    def test_no_match_yields_everything(self) -> None:
        assert list(take_until([1, 2, 3], lambda n: n > 99)) == [1, 2, 3]

    def test_immediate_match_yields_nothing(self) -> None:
        assert list(take_until([1, 2], lambda n: True)) == []

    def test_empty(self) -> None:
        assert list(take_until([], lambda n: True)) == []

    def test_stops_consuming_at_the_match(self) -> None:
        seen: list[int] = []
        result = list(take_until(spy([1, 2, 3, 4, 5], seen), lambda n: n == 3))
        assert result == [1, 2]
        assert seen == [1, 2, 3]  # pulled the match, then stopped — never saw 4 or 5

    def test_works_on_an_infinite_source(self) -> None:
        assert list(take_until(naturals(), lambda n: n == 4)) == [0, 1, 2, 3]


class TestUniqueLazy:
    def test_dedupes_preserving_order(self) -> None:
        assert list(unique_lazy(["b", "a", "b", "c", "a"])) == ["b", "a", "c"]

    def test_already_unique(self) -> None:
        assert list(unique_lazy([1, 2, 3])) == [1, 2, 3]

    def test_empty(self) -> None:
        assert list(unique_lazy([])) == []

    def test_all_duplicates(self) -> None:
        assert list(unique_lazy(["x", "x", "x"])) == ["x"]

    def test_lazy_on_infinite_source(self) -> None:
        repeating = itertools.cycle([1, 2, 3])
        assert list(itertools.islice(unique_lazy(repeating), 3)) == [1, 2, 3]

    def test_yields_before_the_source_is_exhausted(self) -> None:
        seen: list[int] = []
        stream = unique_lazy(spy([1, 2, 3, 4], seen))
        assert next(stream) == 1
        assert seen == [1]


class TestCountdown:
    def test_counts_down(self) -> None:
        assert list(Countdown(3)) == [3, 2, 1]

    def test_zero_yields_nothing(self) -> None:
        assert list(Countdown(0)) == []

    def test_negative_start_raises(self) -> None:
        with pytest.raises(ValueError):
            Countdown(-1)

    def test_is_an_iterator_not_just_an_iterable(self) -> None:
        counter = Countdown(3)
        assert iter(counter) is counter

    def test_is_single_use(self) -> None:
        counter = Countdown(3)
        assert list(counter) == [3, 2, 1]
        assert list(counter) == []

    def test_next_raises_stop_iteration_when_exhausted(self) -> None:
        counter = Countdown(1)
        assert next(counter) == 1
        with pytest.raises(StopIteration):
            next(counter)

    def test_works_with_the_for_protocol(self) -> None:
        assert [n * 2 for n in Countdown(3)] == [6, 4, 2]

    def test_partial_consumption(self) -> None:
        counter = Countdown(5)
        assert next(counter) == 5
        assert list(counter) == [4, 3, 2, 1]


class TestTracker:
    def test_records_enter_and_exit(self) -> None:
        events: list[str] = []
        with Tracker(events):
            events.append("body")
        assert events == ["enter", "body", "exit"]

    def test_enter_returns_self(self) -> None:
        events: list[str] = []
        with Tracker(events) as tracker:
            assert isinstance(tracker, Tracker)

    def test_failed_is_false_on_success(self) -> None:
        events: list[str] = []
        with Tracker(events) as tracker:
            pass
        assert tracker.failed is False

    def test_records_the_exception_type(self) -> None:
        events: list[str] = []
        with pytest.raises(ValueError), Tracker(events):
            raise ValueError("boom")
        assert events == ["enter", "exit:ValueError"]

    def test_does_not_suppress(self) -> None:
        with pytest.raises(KeyError), Tracker([]):
            raise KeyError("nope")

    def test_failed_is_true_after_an_exception(self) -> None:
        tracker = Tracker([])
        with pytest.raises(RuntimeError), tracker:
            raise RuntimeError
        assert tracker.failed is True


class TestCollecting:
    def test_open_and_close(self) -> None:
        log: list[str] = []
        with collecting(log) as active:
            active.append("work")
        assert log == ["open", "work", "close"]

    def test_yields_the_sink_itself(self) -> None:
        log: list[str] = []
        with collecting(log) as active:
            assert active is log

    def test_closes_even_when_the_body_raises(self) -> None:
        log: list[str] = []
        with pytest.raises(ValueError), collecting(log):
            log.append("work")
            raise ValueError("boom")
        assert log == ["open", "work", "close"]

    def test_does_not_suppress(self) -> None:
        with pytest.raises(ZeroDivisionError), collecting([]):
            _ = 1 / 0

    def test_reusable(self) -> None:
        log: list[str] = []
        with collecting(log):
            pass
        with collecting(log):
            pass
        assert log == ["open", "close", "open", "close"]
