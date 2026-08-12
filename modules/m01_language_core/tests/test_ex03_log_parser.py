"""Grader for ex03_log_parser."""

import pytest

from modules.m01_language_core.exercises.ex03_log_parser import (
    MalformedLogLineError,
    count_by_level,
    error_rate_by_service,
    latencies,
    parse_line,
    parse_lines,
    records_for_service,
    slowest,
    summarize,
)

VALID_LINES = [
    '2026-08-11T20:32:10Z INFO service=auth request_id=a1 latency_ms=12 msg="login ok"',
    '2026-08-11T20:32:11Z ERROR service=auth request_id=a2 latency_ms=98 msg="token expired"',
    '2026-08-11T20:32:12Z INFO service=search request_id=a3 latency_ms=45 msg="query ok"',
    '2026-08-11T20:32:13Z ERROR service=db request_id=a4 latency_ms=1500 msg="conn timeout"',
    '2026-08-11T20:32:14Z WARN service=search request_id=a5 latency_ms=250 msg="slow query"',
]

BAD_LINES = [
    "",
    "   ",
    "this line is garbage",
    "2026-08-11T20:32:15Z TRACE service=auth",  # TRACE is not a known level
    "2026-08-11T20:32:16Z INFO service=auth bareword",  # no '=' in a field
    '2026-08-11T20:32:17Z INFO msg="unbalanced',  # shlex cannot split this
    "onlyonetoken",
]

ALL_LINES = [*VALID_LINES, *BAD_LINES]


@pytest.fixture
def records() -> list[dict[str, object]]:
    """A pytest fixture — the @Before/dependency-injected setup you know from JUnit."""
    return parse_lines(VALID_LINES)


class TestParseLine:
    def test_returns_timestamp_level_and_fields(self) -> None:
        assert parse_line('2026-08-11T20:32:10Z INFO service=auth msg="ok"') == {
            "timestamp": "2026-08-11T20:32:10Z",
            "level": "INFO",
            "fields": {"service": "auth", "msg": "ok"},
        }

    def test_quoted_value_keeps_its_spaces(self) -> None:
        record = parse_line('t ERROR msg="token expired for user 7"')
        assert record["fields"]["msg"] == "token expired for user 7"

    def test_value_may_contain_equals_signs(self) -> None:
        record = parse_line("t INFO url=http://x/y?a=b&c=d")
        assert record["fields"]["url"] == "http://x/y?a=b&c=d"

    def test_line_with_no_fields_is_valid(self) -> None:
        assert parse_line("t INFO") == {"timestamp": "t", "level": "INFO", "fields": {}}

    def test_extra_whitespace_is_tolerated(self) -> None:
        record = parse_line("  t   INFO   a=1  ")
        assert record["level"] == "INFO"
        assert record["fields"] == {"a": "1"}

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARN", "ERROR"])
    def test_all_known_levels(self, level: str) -> None:
        assert parse_line(f"t {level}")["level"] == level

    @pytest.mark.parametrize("line", BAD_LINES)
    def test_bad_lines_raise(self, line: str) -> None:
        with pytest.raises(MalformedLogLineError):
            parse_line(line)

    def test_is_a_value_error(self) -> None:
        assert issubclass(MalformedLogLineError, ValueError)

    def test_error_message_includes_the_offending_line(self) -> None:
        with pytest.raises(MalformedLogLineError, match="garbage"):
            parse_line("this line is garbage")


class TestParseLines:
    def test_skips_bad_lines_without_raising(self) -> None:
        assert len(parse_lines(ALL_LINES)) == len(VALID_LINES)

    def test_preserves_order(self) -> None:
        parsed = parse_lines(ALL_LINES)
        assert [r["fields"]["request_id"] for r in parsed] == ["a1", "a2", "a3", "a4", "a5"]

    def test_all_bad_gives_empty_list(self) -> None:
        assert parse_lines(BAD_LINES) == []

    def test_accepts_a_generator(self) -> None:
        assert len(parse_lines(line for line in VALID_LINES)) == 5


class TestAggregations:
    def test_count_by_level_omits_unseen_levels(self, records: list[dict[str, object]]) -> None:
        assert count_by_level(records) == {"INFO": 2, "ERROR": 2, "WARN": 1}

    def test_count_by_level_empty(self) -> None:
        assert count_by_level([]) == {}

    def test_records_for_service(self, records: list[dict[str, object]]) -> None:
        auth = records_for_service(records, "auth")
        assert [r["fields"]["request_id"] for r in auth] == ["a1", "a2"]

    def test_records_for_unknown_service(self, records: list[dict[str, object]]) -> None:
        assert records_for_service(records, "nope") == []

    def test_records_without_service_field_are_excluded(self) -> None:
        mixed = parse_lines(["t INFO service=a", "t INFO other=1"])
        assert len(records_for_service(mixed, "a")) == 1

    def test_latencies_in_input_order(self, records: list[dict[str, object]]) -> None:
        assert latencies(records) == [12, 98, 45, 1500, 250]

    def test_latencies_skips_missing_and_unparseable(self) -> None:
        parsed = parse_lines(["t INFO latency_ms=5", "t INFO x=1", "t INFO latency_ms=zz"])
        assert latencies(parsed) == [5]

    def test_slowest(self, records: list[dict[str, object]]) -> None:
        assert slowest(records, 2) == [("a4", 1500), ("a5", 250)]

    def test_slowest_more_than_available(self, records: list[dict[str, object]]) -> None:
        assert len(slowest(records, 99)) == 5

    def test_slowest_ties_broken_by_request_id(self) -> None:
        parsed = parse_lines(
            [
                "t INFO request_id=z latency_ms=10",
                "t INFO request_id=a latency_ms=10",
            ]
        )
        assert slowest(parsed, 2) == [("a", 10), ("z", 10)]

    def test_slowest_skips_incomplete_records(self) -> None:
        parsed = parse_lines(["t INFO request_id=a", "t INFO latency_ms=5"])
        assert slowest(parsed, 5) == []

    def test_error_rate_by_service(self, records: list[dict[str, object]]) -> None:
        rates = error_rate_by_service(records)
        assert list(rates) == ["auth", "db", "search"]
        assert rates["auth"] == pytest.approx(0.5)
        assert rates["db"] == pytest.approx(1.0)
        assert rates["search"] == pytest.approx(0.0)

    def test_error_rate_empty(self) -> None:
        assert error_rate_by_service([]) == {}


class TestSummarize:
    def test_full_summary(self) -> None:
        summary = summarize(ALL_LINES)
        assert summary == {
            "total": 5,
            "malformed": 7,
            "by_level": {"INFO": 2, "ERROR": 2, "WARN": 1},
            "avg_latency_ms": pytest.approx(381.0),
            "services": ["auth", "db", "search"],
        }

    def test_no_latencies_gives_none(self) -> None:
        summary = summarize(["t INFO service=a"])
        assert summary["avg_latency_ms"] is None

    def test_all_malformed(self) -> None:
        summary = summarize(BAD_LINES)
        assert summary["total"] == 0
        assert summary["malformed"] == len(BAD_LINES)
        assert summary["services"] == []

    def test_works_with_a_single_pass_iterator(self) -> None:
        """`lines` is an Iterable, not a Sequence. Don't iterate it twice."""
        summary = summarize(iter(ALL_LINES))
        assert summary["total"] == 5
        assert summary["malformed"] == 7
