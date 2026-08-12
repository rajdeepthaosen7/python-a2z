# Java → Python translation cheatsheet

Keep this open for the first month. Reread it at the end of Phase 1 — the second read is when
the "Python way" column stops feeling like a workaround and starts feeling correct.

---

## Language constructs

| Java | Python | Note |
| --- | --- | --- |
| `int x = 5;` | `x = 5` | No declaration. `x` is a *name bound to an object*. |
| `final int X = 5;` | `X = 5` | Convention only. `Final[int]` for mypy. Nothing is truly immutable-by-keyword. |
| `String` | `str` | Immutable, Unicode. `bytes` is the separate binary type. |
| `null` | `None` | Singleton. Compare with `is None`, never `== None`. |
| `Optional<T>` | `T \| None` | Native syntax, checked by mypy. |
| `List<T>` | `list[T]` | Mutable, heterogeneous at runtime. |
| `T[]` | `list[T]` or `numpy.ndarray` | Real fixed-type arrays only via NumPy / `array`. |
| `Map<K,V>` | `dict[K,V]` | Insertion-ordered since 3.7. |
| `Set<T>` | `set[T]` | |
| immutable tuple/record | `tuple[A,B]` | Hashable if contents are. |
| `enum` | `enum.Enum` / `StrEnum` | |
| `record Point(int x, int y)` | `@dataclass(frozen=True)` | Module 03. |
| `interface` | `typing.Protocol` | **Structural**, not nominal — no `implements` needed. |
| `abstract class` | `abc.ABC` + `@abstractmethod` | Use when you need shared implementation. |
| `static` method | `@staticmethod` / module-level function | Prefer a module-level function. |
| `class` static field | class attribute | Shared across instances — mutable ones are a classic bug. |
| generics `<T>` | `TypeVar` / `class Box[T]:` (3.12+) | Erased at runtime, like Java. |
| `instanceof` | `isinstance(x, T)` | But prefer duck typing / Protocol. |
| `switch` | `match`/`case` | Structural pattern matching — far more powerful. |
| ternary `a ? b : c` | `b if a else c` | |
| `for (T x : xs)` | `for x in xs:` | |
| classic `for (int i...)` | `for i in range(n):` | Or `enumerate(xs)` when you need index *and* value. |
| `i++` | `i += 1` | No `++` operator. |
| `&&` `\|\|` `!` | `and` `or` `not` | |
| `{ }` blocks | indentation | 4 spaces. Non-negotiable. |
| `try (var r = ...)` | `with open(...) as f:` | Context manager = try-with-resources. |
| `throws` clause | nothing | No checked exceptions. Document in the docstring. |
| `finally` | `finally` | Same. |
| lambda `x -> x * 2` | `lambda x: x * 2` | Single expression only; use a `def` otherwise. |
| `Stream.map/filter` | comprehension or generator | `[f(x) for x in xs if p(x)]` |
| `Optional.orElse` | `x if x is not None else default` or `x or default` | Careful: `or` also catches `0`/`""`. |
| `StringBuilder` | `"".join(parts)` | Never `+=` in a loop. |
| `System.out.println` | `print()` | But use `logging` in real code. |
| `String.format` | f-string: `f"{x:.2f}"` | |
| `package a.b;` | directory + module file | Package identity comes from the filesystem. |
| `import a.b.C;` | `from a.b import C` | |
| `public`/`private` | `name` / `_name` / `__name` | Convention. `_` means "internal", enforced by nothing. |
| `@Override` | nothing | |
| `this` | `self` (explicit first param) | Always written out. |
| `equals`/`hashCode` | `__eq__`/`__hash__` | Same contract, same trap. |
| `toString` | `__str__` (user) / `__repr__` (developer) | Write `__repr__` always. |
| `Comparable` | `__lt__` or `key=` function | `key=` is far more common. |
| `Iterable`/`Iterator` | `__iter__`/`__next__` | Generators give you both for free. |
| `AutoCloseable` | `__enter__`/`__exit__` | |
| checked cast | none needed | |
| `var` | just the name | Python is `var` everywhere, with optional annotations. |

## Ecosystem & tooling

| Java | Python |
| --- | --- |
| Maven / Gradle | `uv` (or Poetry on older teams) |
| `pom.xml` | `pyproject.toml` |
| JUnit 5 | `pytest` |
| Mockito | `unittest.mock` / `pytest-mock` |
| AssertJ | plain `assert` (pytest rewrites it with rich diffs) |
| jqwik | `hypothesis` |
| Testcontainers | `testcontainers` (same project) |
| Checkstyle + SpotBugs + formatter | `ruff` |
| `javac` type errors | `mypy --strict` |
| SLF4J + Logback | `logging` + `structlog` |
| Micrometer | `opentelemetry-*` |
| Spring Boot | FastAPI |
| Spring MVC controllers | FastAPI routers |
| Bean Validation (`@Valid`) | Pydantic v2 |
| Spring DI / `@Autowired` | FastAPI `Depends` (explicit, per-endpoint) |
| Hibernate / JPA | SQLAlchemy 2.0 |
| Flyway / Liquibase | Alembic |
| Jackson | `pydantic` / `json` / `orjson` |
| `CompletableFuture` | `asyncio` + `await` |
| `ExecutorService` | `concurrent.futures.ThreadPoolExecutor` |
| Virtual threads (Loom) | async, or free-threaded CPython 3.13+ |
| Jar / fat jar | wheel (`.whl`) / container image |
| Spring Boot Actuator | write the `/health` endpoint yourself |
| Lombok | `@dataclass` / `attrs` (built in, no annotation processor) |

## Mental model shifts that actually matter

1. **Names, not variables.** `a = b` never copies. It binds a second name to the same object.
   `id(x)` is your `System.identityHashCode`.

2. **Mutable default arguments are evaluated once**, at function definition. `def f(xs=[])` is a
   shared-state bug, and `ruff` rule `B006` will catch it. This has no Java equivalent and it
   bites everyone once.

3. **There are no checked exceptions and no `throws`.** Nothing forces you to handle anything.
   Discipline comes from the docstring and from tests.

4. **EAFP over LBYL.** "Easier to Ask Forgiveness than Permission." Idiomatic Python calls the
   thing and catches the exception rather than pre-checking. `try/except` is cheap here, unlike
   JVM exception construction with stack-trace capture.

5. **Duck typing beats interfaces.** If it has `.read()`, it's a file for your purposes. Declare
   that expectation with `Protocol` for the type checker, but don't demand inheritance.

6. **Everything is an object, including classes, functions, and modules.** Functions are values;
   passing and returning them is normal, not clever.

7. **The GIL is real but narrower than the folklore.** One thread executes Python bytecode at a
   time, so CPU-bound threading doesn't scale — but I/O releases the GIL, so threads *are* fine
   for I/O. Use processes for CPU work, async for high-concurrency I/O. Module 07.

8. **The stdlib is your framework.** Before adding a dependency, check `itertools`,
   `collections`, `functools`, `pathlib`, `dataclasses`, `contextlib`. Python teams add
   dependencies far more reluctantly than Spring teams add starters.

9. **Explicit beats implicit.** No classpath scanning, no annotation magic, no proxies wrapping
   your beans. Python's answer to `@Transactional` is a `with` block you can see. This feels like
   a downgrade for two weeks, then like a relief.

10. **`__init__.py`, not the package declaration.** Package structure comes from directories, and
    imports are executed top-to-bottom at runtime. Circular imports are a runtime error, not a
    compile error.
