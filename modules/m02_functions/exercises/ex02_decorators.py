"""Exercise 02 — the decorators you will actually write in production.

Retry, cache, trace, deprecate, validate. Every one of these has a Spring
annotation equivalent, and every one of them is under 15 lines here.

Run:  uv run pytest modules/m02_functions/tests/test_ex02_decorators.py -x -q

Constraints:
  * Every function decorator uses `functools.wraps`. This is tested.
  * Decorator factories validate their arguments at DECORATION time, not at
    call time. Failing fast at import beats failing at 3am.
  * No `time.sleep` anywhere — tests must stay fast and deterministic.
"""

import functools  # noqa: F401  (you'll need it)
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


def default_on_error(default: T, *exceptions: type[BaseException]) -> Callable[..., Any]:
    """Decorator factory: swallow the listed exceptions and return `default`.

    If no exception types are given, catch `Exception` (never BaseException —
    that would swallow KeyboardInterrupt and SystemExit).

    Exceptions NOT listed must propagate unchanged.

        @default_on_error(0, ValueError)
        def parse(text: str) -> int:
            return int(text)

        parse("12")     # 12
        parse("abc")    # 0
    """
    raise NotImplementedError


def retry(
    attempts: int, *, exceptions: tuple[type[BaseException], ...] = (Exception,)
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator factory: re-invoke the function until it succeeds.

    `attempts` is the TOTAL number of tries, not the number of retries.
    On the final failure, re-raise the exception unchanged (keep the original
    traceback — do not wrap it).

    Only the listed exception types trigger a retry; anything else propagates
    immediately.

    Raises:
        ValueError: at decoration time, if attempts < 1.

    This is @Retryable. In production you'd use `tenacity` for the backoff and
    jitter, but you should be able to write the core in your sleep.
    """
    raise NotImplementedError


def trace(sink: list[str]) -> Callable[..., Any]:
    """Decorator factory: append a call log to `sink`.

    Exactly two entries per call, in this format:

        on entry:    "name(1, 2, key='v')"
        on success:  "name -> 42"
        on failure:  "name !! ValueError"        (then re-raise)

    The argument list is positional args first (as `repr`), then keyword
    arguments as `key=repr(value)`, joined with ", ". Use the function's
    `__name__`. Return values and argument values both use `repr`.

        >>> log = []
        >>> @trace(log)
        ... def add(a, b, scale=1): return (a + b) * scale
        >>> add(1, 2, scale=10)
        30
        >>> log
        ["add(1, 2, scale=10)", 'add -> 30']

    Poor-man's distributed tracing. Module 18 replaces it with OpenTelemetry
    spans, but the shape is identical.
    """
    raise NotImplementedError


def deprecated(reason: str) -> Callable[..., Any]:
    """Decorator factory: emit a DeprecationWarning, then call through normally.

    The warning message must contain both the function's `__name__` and the
    `reason` text. Pass `stacklevel=2` so the warning points at the CALLER's
    line, not at your wrapper — that's the difference between a useful warning
    and a useless one.

    Use `warnings.warn(msg, DeprecationWarning, stacklevel=2)`.
    """
    raise NotImplementedError


def validate_positive(fn: Callable[..., T]) -> Callable[..., T]:
    """Decorator: reject non-positive numeric arguments.

    Check every positional argument and every keyword-argument VALUE. If any
    of them is an `int` or `float` and is <= 0, raise ValueError with the
    offending value in the message. Non-numeric arguments are ignored.

    `bool` must NOT be treated as numeric, even though `isinstance(True, int)`
    is True in Python. Handle that explicitly — it's a real bug class.
    """
    raise NotImplementedError


def cache_by(key_fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator factory: memoize, keyed by `key_fn(*args, **kwargs)`.

    Needed whenever arguments aren't hashable or aren't the right cache key —
    e.g. caching an LLM call by a normalized prompt rather than by the whole
    request object. You'll want exactly this in Module 19.

    Expose a `cache_clear()` callable on the wrapper.

        @cache_by(lambda user: user["id"])
        def load(user: dict) -> str: ...
    """
    raise NotImplementedError


def singleton(cls: type[T]) -> Callable[..., T]:
    """Class decorator: always return the same instance.

    `__init__` must run exactly once, on the first construction. Later calls
    return the existing instance and ignore their arguments.

        @singleton
        class Config: ...

        Config() is Config()    # True

    Python's honest answer to the singleton bean. Note what you give up: the
    decorated name is no longer a class, so `isinstance` against it fails.
    That's why a module-level instance is usually the better idiom — modules
    are already singletons.
    """
    raise NotImplementedError


def add_repr(cls: type[T]) -> type[T]:
    """Class decorator: give a class a `__repr__` built from its instance dict.

    Format: "ClassName(field=value, other=value)" with values as `repr`, in
    the attribute insertion order given by `vars(instance)`.

        @add_repr
        class Point:
            def __init__(self, x, y): self.x, self.y = x, y

        repr(Point(1, "a"))    # "Point(x=1, y='a')"

    Return the SAME class object (mutated), not a new one.

    This is Lombok's @ToString in six lines, with no annotation processor.
    Module 03 shows you the real answer: @dataclass gives you this plus
    __eq__, __hash__, and ordering, for free.
    """
    raise NotImplementedError
