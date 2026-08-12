import shlex
from collections import Counter
from collections.abc import Iterable
from typing import Any

LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")

LogRecord = dict[str, Any]


class MalformedLogLineError(ValueError):
    pass


def parse_line(line: str) -> LogRecord:
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        raise MalformedLogLineError(f"cannot tokenize log line: {line!r}") from exc
    if len(parts) < 2:
        raise MalformedLogLineError(f"expected timestamp and level in line: {line!r}")
    timestamp, level, *rest = parts
    if level not in LEVELS:
        raise MalformedLogLineError(f"unknown level {level!r} in line: {line!r}")
    fields: dict[str, str] = {}
    for token in rest:
        key, sep, value = token.partition("=")
        if not sep:
            raise MalformedLogLineError(f"field {token!r} has no '=' in line: {line!r}")
        fields[key] = value
    return {"timestamp": timestamp, "level": level, "fields": fields}


def parse_lines(lines: Iterable[str]) -> list[LogRecord]:
    records: list[LogRecord] = []
    for line in lines:
        try:
            records.append(parse_line(line))
        except MalformedLogLineError:
            continue
    return records


def count_by_level(records: Iterable[LogRecord]) -> dict[str, int]:
    return dict(Counter(record["level"] for record in records))


def records_for_service(records: Iterable[LogRecord], service: str) -> list[LogRecord]:
    return [r for r in records if r["fields"].get("service") == service]


def latencies(records: Iterable[LogRecord]) -> list[int]:
    out: list[int] = []
    for record in records:
        raw = record["fields"].get("latency_ms")
        if raw is None:
            continue
        try:
            out.append(int(raw))
        except ValueError:
            continue
    return out


def slowest(records: Iterable[LogRecord], n: int) -> list[tuple[str, int]]:
    pairs: list[tuple[str, int]] = []
    for record in records:
        fields = record["fields"]
        request_id, raw = fields.get("request_id"), fields.get("latency_ms")
        if request_id is None or raw is None:
            continue
        try:
            pairs.append((request_id, int(raw)))
        except ValueError:
            continue
    return sorted(pairs, key=lambda p: (-p[1], p[0]))[:n]


def error_rate_by_service(records: Iterable[LogRecord]) -> dict[str, float]:
    totals: Counter[str] = Counter()
    errors: Counter[str] = Counter()
    for record in records:
        service = record["fields"].get("service")
        if service is None:
            continue
        totals[service] += 1
        if record["level"] == "ERROR":
            errors[service] += 1
    return {service: errors[service] / totals[service] for service in sorted(totals)}


def summarize(lines: Iterable[str]) -> dict[str, Any]:
    materialized = list(lines)
    records = parse_lines(materialized)
    lats = latencies(records)
    services = sorted({r["fields"]["service"] for r in records if "service" in r["fields"]})
    return {
        "total": len(records),
        "malformed": len(materialized) - len(records),
        "by_level": count_by_level(records),
        "avg_latency_ms": sum(lats) / len(lats) if lats else None,
        "services": services,
    }
