"""Reference solution — read only after your own version is green."""

import functools
import warnings
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


def default_on_error(default: T, *exceptions: type[BaseException]) -> Callable[..., Any]:
    caught = exceptions or (Exception,)

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except caught:
                return default

        return wrapper

    return decorator


def retry(
    attempts: int, *, exceptions: tuple[type[BaseException], ...] = (Exception,)
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    if attempts < 1:
        raise ValueError(f"attempts must be >= 1, got {attempts}")

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == attempts:
                        raise  # bare re-raise keeps the original traceback
            raise AssertionError("unreachable")

        return wrapper

    return decorator


def trace(sink: list[str]) -> Callable[..., Any]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            rendered = ", ".join(
                [*(repr(a) for a in args), *(f"{k}={v!r}" for k, v in kwargs.items())]
            )
            sink.append(f"{fn.__name__}({rendered})")
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:
                sink.append(f"{fn.__name__} !! {type(exc).__name__}")
                raise
            sink.append(f"{fn.__name__} -> {result!r}")
            return result

        return wrapper

    return decorator


def deprecated(reason: str) -> Callable[..., Any]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{fn.__name__}() is deprecated: {reason}",
                DeprecationWarning,
                stacklevel=2,  # point at the caller, not at this wrapper
            )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def validate_positive(fn: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        for value in (*args, *kwargs.values()):
            # bool is a subclass of int — exclude it before the numeric check.
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)) and value <= 0:
                raise ValueError(f"expected a positive number, got {value!r}")
        return fn(*args, **kwargs)

    return wrapper


def cache_by(key_fn: Callable[..., Any]) -> Callable[..., Any]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        cache: dict[Any, Any] = {}

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = key_fn(*args, **kwargs)
            if key not in cache:
                cache[key] = fn(*args, **kwargs)
            return cache[key]

        wrapper.cache_clear = cache.clear  # type: ignore[attr-defined]
        return wrapper

    return decorator


def singleton(cls: type[T]) -> Callable[..., T]:
    instance: T | None = None

    def get_instance(*args: Any, **kwargs: Any) -> T:
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance

    return get_instance


def add_repr(cls: type[T]) -> type[T]:
    def __repr__(self: object) -> str:  # noqa: N807
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({fields})"

    cls.__repr__ = __repr__  # type: ignore[method-assign]
    return cls
