"""Grader for ex02_decorators."""

import pytest

from modules.m02_functions.exercises.ex02_decorators import (
    add_repr,
    cache_by,
    default_on_error,
    deprecated,
    retry,
    singleton,
    trace,
    validate_positive,
)


class TestDefaultOnError:
    def test_returns_value_on_success(self) -> None:
        @default_on_error(0, ValueError)
        def parse(text: str) -> int:
            return int(text)

        assert parse("12") == 12

    def test_returns_default_on_listed_exception(self) -> None:
        @default_on_error(0, ValueError)
        def parse(text: str) -> int:
            return int(text)

        assert parse("abc") == 0

    def test_unlisted_exception_propagates(self) -> None:
        @default_on_error(0, ValueError)
        def boom() -> int:
            raise KeyError("nope")

        with pytest.raises(KeyError):
            boom()

    def test_no_exception_types_catches_exception(self) -> None:
        @default_on_error("fallback")
        def boom() -> str:
            raise RuntimeError("anything")

        assert boom() == "fallback"

    def test_does_not_swallow_base_exception(self) -> None:
        """BaseException subclasses like KeyboardInterrupt must get through."""

        @default_on_error("fallback")
        def interrupted() -> str:
            raise KeyboardInterrupt

        with pytest.raises(KeyboardInterrupt):
            interrupted()

    def test_multiple_exception_types(self) -> None:
        @default_on_error(None, ValueError, KeyError)
        def boom(exc: type[BaseException]) -> str:
            raise exc

        assert boom(ValueError) is None
        assert boom(KeyError) is None

    def test_preserves_metadata(self) -> None:
        @default_on_error(0)
        def documented() -> int:
            """Doc."""
            return 1

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Doc."


class TestRetry:
    def test_succeeds_first_time(self) -> None:
        calls = []

        @retry(3)
        def work() -> str:
            calls.append(1)
            return "ok"

        assert work() == "ok"
        assert len(calls) == 1

    def test_retries_until_success(self) -> None:
        calls: list[int] = []

        @retry(3)
        def flaky() -> str:
            calls.append(1)
            if len(calls) < 3:
                raise ValueError("transient")
            return "ok"

        assert flaky() == "ok"
        assert len(calls) == 3

    def test_reraises_after_exhausting_attempts(self) -> None:
        calls: list[int] = []

        @retry(2)
        def always_fails() -> None:
            calls.append(1)
            raise ValueError("permanent")

        with pytest.raises(ValueError, match="permanent"):
            always_fails()
        assert len(calls) == 2

    def test_attempts_is_total_tries_not_extra_retries(self) -> None:
        calls: list[int] = []

        @retry(1)
        def always_fails() -> None:
            calls.append(1)
            raise ValueError

        with pytest.raises(ValueError):
            always_fails()
        assert len(calls) == 1

    def test_only_listed_exceptions_are_retried(self) -> None:
        calls: list[int] = []

        @retry(3, exceptions=(ValueError,))
        def wrong_error() -> None:
            calls.append(1)
            raise TypeError("not retryable")

        with pytest.raises(TypeError):
            wrong_error()
        assert len(calls) == 1

    @pytest.mark.parametrize("attempts", [0, -1])
    def test_invalid_attempts_raises_at_decoration_time(self, attempts: int) -> None:
        with pytest.raises(ValueError):
            retry(attempts)

    def test_arguments_are_forwarded_on_every_attempt(self) -> None:
        seen: list[tuple[int, int]] = []

        @retry(2)
        def add(a: int, *, b: int) -> int:
            seen.append((a, b))
            if len(seen) < 2:
                raise ValueError
            return a + b

        assert add(1, b=2) == 3
        assert seen == [(1, 2), (1, 2)]

    def test_preserves_metadata(self) -> None:
        @retry(2)
        def documented() -> None:
            """Doc."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Doc."


class TestTrace:
    def test_logs_entry_and_result(self) -> None:
        log: list[str] = []

        @trace(log)
        def add(a: int, b: int, scale: int = 1) -> int:
            return (a + b) * scale

        assert add(1, 2, scale=10) == 30
        assert log == ["add(1, 2, scale=10)", "add -> 30"]

    def test_positional_only(self) -> None:
        log: list[str] = []

        @trace(log)
        def add(a: int, b: int) -> int:
            return a + b

        add(1, 2)
        assert log == ["add(1, 2)", "add -> 3"]

    def test_no_arguments(self) -> None:
        log: list[str] = []

        @trace(log)
        def nothing() -> None:
            return None

        nothing()
        assert log == ["nothing()", "nothing -> None"]

    def test_uses_repr_for_values(self) -> None:
        log: list[str] = []

        @trace(log)
        def echo(text: str) -> str:
            return text

        echo("hi")
        assert log == ["echo('hi')", "echo -> 'hi'"]

    def test_logs_failure_and_reraises(self) -> None:
        log: list[str] = []

        @trace(log)
        def boom() -> None:
            raise ValueError("bad")

        with pytest.raises(ValueError):
            boom()
        assert log == ["boom()", "boom !! ValueError"]

    def test_accumulates_across_calls(self) -> None:
        log: list[str] = []

        @trace(log)
        def work(n: int) -> int:
            return n

        work(1)
        work(2)
        assert len(log) == 4

    def test_preserves_metadata(self) -> None:
        @trace([])
        def documented() -> None:
            """Doc."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Doc."


class TestDeprecated:
    def test_warns(self) -> None:
        @deprecated("use new_api instead")
        def old_api() -> str:
            return "result"

        with pytest.warns(DeprecationWarning):
            assert old_api() == "result"

    def test_message_contains_name_and_reason(self) -> None:
        @deprecated("use new_api instead")
        def old_api() -> str:
            return "result"

        with pytest.warns(DeprecationWarning) as record:
            old_api()
        message = str(record[0].message)
        assert "old_api" in message
        assert "use new_api instead" in message

    def test_arguments_are_forwarded(self) -> None:
        @deprecated("gone")
        def add(a: int, b: int = 0) -> int:
            return a + b

        with pytest.warns(DeprecationWarning):
            assert add(1, b=2) == 3

    def test_preserves_metadata(self) -> None:
        @deprecated("gone")
        def documented() -> None:
            """Doc."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Doc."


class TestValidatePositive:
    def test_allows_positive(self) -> None:
        @validate_positive
        def area(width: float, height: float) -> float:
            return width * height

        assert area(2, 3.5) == 7.0

    @pytest.mark.parametrize("bad", [0, -1, -0.5, 0.0])
    def test_rejects_non_positive_positional(self, bad: float) -> None:
        @validate_positive
        def scale(value: float) -> float:
            return value

        with pytest.raises(ValueError):
            scale(bad)

    def test_rejects_non_positive_keyword(self) -> None:
        @validate_positive
        def scale(*, factor: float = 1.0) -> float:
            return factor

        with pytest.raises(ValueError):
            scale(factor=-2)

    def test_message_includes_the_offending_value(self) -> None:
        @validate_positive
        def scale(value: float) -> float:
            return value

        with pytest.raises(ValueError, match="-7"):
            scale(-7)

    def test_non_numeric_arguments_are_ignored(self) -> None:
        @validate_positive
        def label(name: str, count: int, tags: list[str] | None = None) -> str:
            return f"{name}:{count}:{tags}"

        assert label("x", 1, tags=[]) == "x:1:[]"

    def test_bool_is_not_treated_as_numeric(self) -> None:
        """isinstance(False, int) is True in Python. Handle it explicitly."""

        @validate_positive
        def toggle(flag: bool) -> bool:
            return flag

        assert toggle(False) is False

    def test_preserves_metadata(self) -> None:
        @validate_positive
        def documented() -> None:
            """Doc."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Doc."


class TestCacheBy:
    def test_caches_on_custom_key(self) -> None:
        calls: list[str] = []

        @cache_by(lambda user: user["id"])
        def load(user: dict[str, object]) -> str:
            calls.append(str(user["id"]))
            return f"loaded {user['id']}"

        # Same id, different (unhashable) dict objects -> one underlying call.
        assert load({"id": "u1", "seen": 1}) == "loaded u1"
        assert load({"id": "u1", "seen": 2}) == "loaded u1"
        assert calls == ["u1"]

    def test_different_keys_are_separate_entries(self) -> None:
        calls: list[str] = []

        @cache_by(lambda user: user["id"])
        def load(user: dict[str, object]) -> str:
            calls.append(str(user["id"]))
            return f"loaded {user['id']}"

        load({"id": "a"})
        load({"id": "b"})
        load({"id": "a"})
        assert calls == ["a", "b"]

    def test_key_function_sees_all_arguments(self) -> None:
        @cache_by(lambda *args, **kwargs: (args, tuple(sorted(kwargs.items()))))
        def add(a: int, b: int = 0) -> int:
            return a + b

        assert add(1, b=2) == 3
        assert add(1, b=2) == 3
        assert add(1, b=3) == 4

    def test_cache_clear(self) -> None:
        calls: list[int] = []

        @cache_by(lambda n: n)
        def work(n: int) -> int:
            calls.append(n)
            return n

        work(1)
        work(1)
        assert calls == [1]
        work.cache_clear()
        work(1)
        assert calls == [1, 1]

    def test_preserves_metadata(self) -> None:
        @cache_by(lambda: None)
        def documented() -> None:
            """Doc."""

        assert documented.__name__ == "documented"
        assert documented.__doc__ == "Doc."


class TestSingleton:
    def test_same_instance(self) -> None:
        @singleton
        class Config:
            def __init__(self) -> None:
                self.value = 1

        assert Config() is Config()

    def test_init_runs_once(self) -> None:
        inits: list[int] = []

        @singleton
        class Service:
            def __init__(self, name: str = "default") -> None:
                inits.append(1)
                self.name = name

        first = Service("a")
        second = Service("b")  # arguments ignored — instance already exists
        assert len(inits) == 1
        assert first.name == "a"
        assert second.name == "a"

    def test_separate_classes_have_separate_instances(self) -> None:
        @singleton
        class A: ...

        @singleton
        class B: ...

        assert A() is not B()  # type: ignore[comparison-overlap]
        assert A() is A()


class TestAddRepr:
    def test_repr_format(self) -> None:
        @add_repr
        class Point:
            def __init__(self, x: int, y: str) -> None:
                self.x = x
                self.y = y

        assert repr(Point(1, "a")) == "Point(x=1, y='a')"

    def test_attribute_order_follows_assignment(self) -> None:
        @add_repr
        class Reversed:
            def __init__(self) -> None:
                self.z = 1
                self.a = 2

        assert repr(Reversed()) == "Reversed(z=1, a=2)"

    def test_no_attributes(self) -> None:
        @add_repr
        class Empty: ...

        assert repr(Empty()) == "Empty()"

    def test_returns_the_same_class_object(self) -> None:
        class Original: ...

        assert add_repr(Original) is Original

    def test_instances_are_still_normal(self) -> None:
        @add_repr
        class Counter:
            def __init__(self) -> None:
                self.n = 0

            def bump(self) -> None:
                self.n += 1

        counter = Counter()
        counter.bump()
        assert isinstance(counter, Counter)
        assert repr(counter) == "Counter(n=1)"
