"""Exercise 03 — a real log parser: parsing, exceptions, aggregation.

This is the closest thing in Module 01 to actual production work. The input is
logfmt, the structured-logging format you'll emit from Athena in Module 08.

Line format:
    <timestamp> <LEVEL> key=value key=value ... msg="may contain spaces"

Example:
    2026-08-11T20:32:10Z ERROR service=auth request_id=a1 latency_ms=42 msg="token expired"

Run:  uv run pytest modules/m01_language_core/tests/test_ex03_log_parser.py -x -q

Constraints:
  * Use `shlex.split` to tokenize a line — it understands the quoting rules so
    you don't hand-roll a parser. Go read `help(shlex.split)` first.
  * `parse_line` raises; `parse_lines` never raises. That split (a strict
    primitive plus a lenient batch wrapper) is a pattern you'll reuse forever.
  * Use `str.partition` or `split("=", 1)` for key=value — values can contain '='.
"""

from collections.abc import Iterable
from typing import Any

LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")

LogRecord = dict[str, Any]
"""Shape: {"timestamp": str, "level": str, "fields": dict[str, str]}.

In Module 03 you will replace this dict with a frozen dataclass, and in
Module 05 with a Pydantic model. Feel the pain of the dict first.
"""


class MalformedLogLineError(ValueError):
    """Raised when a line cannot be parsed.

    Subclasses ValueError so that callers who only care that "the value was
    bad" can catch the stdlib type, while callers who care about logs
    specifically can catch this one. Design your exception hierarchy this way.

    The `Error` suffix is PEP 8 convention and ruff enforces it (rule N818) —
    the same instinct as Java's `*Exception` suffix.
    """


def parse_line(line: str) -> LogRecord:
    """Parse one log line into a LogRecord.

    >>> parse_line('2026-08-11T20:32:10Z INFO service=auth msg="ok"')
    {'timestamp': '2026-08-11T20:32:10Z', 'level': 'INFO',
     'fields': {'service': 'auth', 'msg': 'ok'}}

    Raises:
        MalformedLogLineError: if the line is blank or whitespace-only; if it has
            fewer than two whitespace-separated tokens; if the second token is
            not one of LEVELS; if any remaining token has no '='; or if
            shlex.split fails on unbalanced quotes.

    Include the offending line in the error message, with !r. Every minute you
    spend on error messages now, you save tenfold at 2am later.
    """
    raise NotImplementedError


def parse_lines(lines: Iterable[str]) -> list[LogRecord]:
    """Parse every line, silently skipping the ones that fail.

    Never raises. This is the lenient batch counterpart to parse_line.

    >>> len(parse_lines(["2026-01-01T00:00:00Z INFO a=b", "garbage", ""]))
    1
    """
    raise NotImplementedError


def count_by_level(records: Iterable[LogRecord]) -> dict[str, int]:
    """Count records per level. Levels with zero records are omitted.

    >>> count_by_level(parse_lines(["t INFO a=b", "t ERROR a=b", "t INFO a=b"]))
    {'INFO': 2, 'ERROR': 1}
    """
    raise NotImplementedError


def records_for_service(records: Iterable[LogRecord], service: str) -> list[LogRecord]:
    """Return records whose fields contain service=<service>, input order preserved.

    Records with no `service` field are excluded.
    """
    raise NotImplementedError


def latencies(records: Iterable[LogRecord]) -> list[int]:
    """Return every parseable latency_ms value, in input order.

    Records without a latency_ms field, or whose value is not an integer, are
    skipped — do not raise. This is EAFP: try int(), catch ValueError.

    >>> latencies(parse_lines(["t INFO latency_ms=5", "t INFO x=1", "t INFO latency_ms=zz"]))
    [5]
    """
    raise NotImplementedError


def slowest(records: Iterable[LogRecord], n: int) -> list[tuple[str, int]]:
    """Return the n slowest (request_id, latency_ms) pairs.

    Sort by latency descending, then request_id ascending. Records missing
    either field, or with an unparseable latency, are skipped.
    """
    raise NotImplementedError


def error_rate_by_service(records: Iterable[LogRecord]) -> dict[str, float]:
    """Map each service to its fraction of ERROR-level records.

    Only records with a `service` field count. A service with no errors still
    appears, with rate 0.0. Result keys are sorted alphabetically.

    >>> error_rate_by_service(parse_lines(["t ERROR service=a", "t INFO service=a"]))
    {'a': 0.5}
    """
    raise NotImplementedError


def summarize(lines: Iterable[str]) -> dict[str, Any]:
    """Produce a single summary dict over raw log lines.

    Returns exactly these keys:
        "total":          number of lines that parsed successfully
        "malformed":      number of lines that did not parse
        "by_level":       result of count_by_level
        "avg_latency_ms": mean of latencies(), or None when there are none
        "services":       sorted list of distinct service names

    Note `lines` is an Iterable, so you may only iterate it ONCE. Materialize
    it first if you need two passes — this is a real bug class in Python, and
    the reason `list(...)` at a function boundary is often the right call.
    """
    raise NotImplementedError
