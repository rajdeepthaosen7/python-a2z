"""Decorators from first principles: what Spring AOP is, minus the container.

Run me:  uv run python modules/m02_functions/examples/05_decorators.py
"""

import functools
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


# ---- 1. The simplest possible decorator ---------------------------------
def shout(fn: Callable[..., str]) -> Callable[..., str]:
    def wrapper(*args: Any, **kwargs: Any) -> str:
        return fn(*args, **kwargs).upper() + "!"

    return wrapper


@shout
def greet(name: str) -> str:
    """Say hello."""
    return f"hello {name}"


# `@shout` above is EXACTLY this:
def greet_manual(name: str) -> str:
    return f"hello {name}"


greet_manual = shout(greet_manual)


# ---- 2. Why functools.wraps is mandatory --------------------------------
def broken_decorator(fn: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return fn(*args, **kwargs)

    return wrapper


def good_decorator(fn: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(fn)  # copies __name__, __doc__, __module__, __wrapped__
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return fn(*args, **kwargs)

    return wrapper


@broken_decorator
def alpha() -> str:
    """Alpha's docstring."""
    return "a"


@good_decorator
def beta() -> str:
    """Beta's docstring."""
    return "b"


# ---- 3. State on the wrapper -------------------------------------------
def count_calls(fn: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        wrapper.call_count += 1  # type: ignore[attr-defined]
        return fn(*args, **kwargs)

    wrapper.call_count = 0  # type: ignore[attr-defined]
    return wrapper


@count_calls
def work(n: int) -> int:
    return n * 2


# ---- 4. A decorator FACTORY (a decorator with arguments) ----------------
def retry(attempts: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Three nested functions. Memorize this shape.

    retry(3)          -> returns `decorator`
    decorator(fn)     -> returns `wrapper`
    wrapper(*a, **k)  -> the thing that actually runs
    """
    if attempts < 1:  # validate at DECORATION time, not call time
        raise ValueError(f"attempts must be >= 1, got {attempts}")

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except ValueError:
                    print(f"     attempt {attempt} failed")
                    if attempt == attempts:
                        raise
            raise AssertionError("unreachable")

        return wrapper

    return decorator


_calls = 0


@retry(3)
def flaky() -> str:
    global _calls
    _calls += 1
    if _calls < 3:
        raise ValueError("transient")
    return "succeeded"


# ---- 5. Stacking: applied bottom-up ------------------------------------
def outer(fn: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        print("     outer before")
        result = fn(*args, **kwargs)
        print("     outer after")
        return result

    return wrapper


def inner(fn: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        print("     inner before")
        result = fn(*args, **kwargs)
        print("     inner after")
        return result

    return wrapper


@outer
@inner
def target() -> str:
    print("     target body")
    return "done"


# equivalent to: target = outer(inner(target))


def main() -> None:
    print("1)", greet("ada"), "|", greet_manual("bob"))

    # ---- metadata ----
    print("2) broken:", alpha.__name__, alpha.__doc__)
    print("3) good:  ", beta.__name__, beta.__doc__)
    print("4) unwrap:", beta.__wrapped__.__name__)  # type: ignore[attr-defined]
    # Without wraps, `alpha.__name__` is 'wrapper'. That breaks pytest test
    # discovery, FastAPI route naming, logging, and every traceback you'll read.

    # ---- state ----
    work(1)
    work(2)
    print("5)", work.call_count, work.__name__)  # type: ignore[attr-defined]

    # ---- factory ----
    print("6) retrying:")
    print("  ", flaky())
    try:
        retry(0)
    except ValueError as exc:
        print("7)", exc, "(raised at decoration time — fail fast)")

    # ---- stacking ----
    print("8) stack order:")
    target()
    # outer wraps inner wraps target. Read decorator stacks INSIDE-OUT.
    # Practical consequence: @count_calls above @retry counts logical calls;
    # below @retry it counts attempts. Order is a design decision.

    # ---- 6. Decorating methods ------------------------------------------
    class Service:
        @count_calls
        def handle(self, request: str) -> str:
            return f"handled {request}"

        @staticmethod
        def helper() -> str:
            return "static"

        @property  # property is itself a decorator
        def name(self) -> str:
            return "svc"

    svc = Service()
    svc.handle("a")
    svc.handle("b")
    print("9)", Service.handle.call_count, svc.name, Service.helper())  # type: ignore[attr-defined]
    # `self` arrives as args[0] — *args/**kwargs forwarding handles it for free.
    # Note the counter lives on the FUNCTION, so it's shared across instances.

    # ---- 7. Real stdlib decorators you already have ---------------------
    @functools.cache  # this is @Cacheable. One line.
    def fib(n: int) -> int:
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    print("10)", fib(60), fib.cache_info())
    # Without the cache that's ~2^60 calls. With it, 61.


if __name__ == "__main__":
    main()
