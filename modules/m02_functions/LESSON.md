# Module 02 — Functions & Decorators (Week 2)

> **Prerequisite:** Module 01 tests green.
> **Time:** 4 weeknights × ~1.75h + weekend project checkpoint.
> **Goal:** functions as values, and decorators as the tool that replaces most of Spring AOP.

This is the module where Python stops looking like a scripting language. Everything you know as
`@Transactional`, `@Cacheable`, `@Retryable`, `@Async` — annotation plus a proxy plus a container
that weaves them together — is, in Python, a function that takes a function and returns a
function. Twelve lines, no magic, fully debuggable. Once decorators click, a large fraction of
the Python ecosystem stops being mysterious.

---

## Night 1 — Functions are objects

**Run:** `examples/01_first_class_functions.py`

A `def` statement creates a function object and binds it to a name. That's all. The object has
attributes you can inspect and pass around:

```python
def greet(name: str) -> str:
    """Say hello."""
    return f"hello {name}"


greet.__name__  # 'greet'
greet.__doc__  # 'Say hello.'
greet.__module__
greet.__annotations__  # {'name': <class 'str'>, 'return': <class 'str'>}
greet.tag = "x"  # yes, you can attach arbitrary attributes
```

So all of this is ordinary:

```python
say = greet  # alias, no copy
handlers = {"greet": greet}  # dispatch table instead of a switch


def call_twice(fn, arg):  # take a function as a parameter
    return fn(fn(arg))


def adder(n):  # return a function
    def add(x):
        return x + n

    return add
```

### The dispatch-table pattern

This replaces the Strategy pattern, and often an entire interface hierarchy:

```python
FORMATTERS: dict[str, Callable[[dict], str]] = {
    "json": to_json,
    "csv": to_csv,
    "table": to_table,
}


def render(data: dict, fmt: str) -> str:
    try:
        return FORMATTERS[fmt](data)
    except KeyError:
        raise ValueError(f"unknown format {fmt!r}, expected one of {sorted(FORMATTERS)}") from None
```

In Java you'd define an interface, three implementing classes, and register them in a map — or
let Spring scan for them. Here the functions *are* the implementations. Reach for a class only
when you need state or a shared base implementation.

### Typing a callable

```python
from collections.abc import Callable

Transform = Callable[[str], str]  # takes str, returns str
Predicate = Callable[[int], bool]
Handler = Callable[..., None]  # any args, returns None
```

Import `Callable` from `collections.abc`, not `typing` — the `typing` version is deprecated.

### `lambda` — and why you'll rarely use it

A `lambda` is a single-expression anonymous function. It cannot contain statements, so no
assignment, no `if/raise`, no multiple lines.

```python
sorted(words, key=lambda w: (len(w), w))  # good use: throwaway key function
```

Never assign a lambda to a name (`f = lambda x: ...`) — that's just a worse `def` with no name in
tracebacks. `ruff` rule `E731` flags it.

---

## Night 2 — Parameters, and the one trap that gets everyone

**Run:** `examples/02_args_kwargs.py`, then `examples/03_default_arg_trap.py`

### The full parameter grammar

```python
def f(pos_only, /, standard, *args, kw_only, **kwargs) -> None: ...
```

| Syntax | Meaning |
| --- | --- |
| before `/` | positional-only — caller cannot use the name |
| between `/` and `*` | positional *or* keyword (the default) |
| `*args` | collects extra positionals into a tuple |
| after `*` or `*args` | **keyword-only** — caller must name it |
| `**kwargs` | collects extra keywords into a dict |

The one to actually use daily is the bare `*`:

```python
def connect(host: str, port: int, *, timeout: float = 5.0, retries: int = 3) -> None: ...


connect("db", 5432, timeout=1.0)  # fine
connect("db", 5432, 1.0)  # TypeError — and that's the point
```

Make every optional/boolean/config parameter keyword-only. `render(data, True, False)` is
unreadable and un-refactorable; `render(data, sort=True, header=False)` is self-documenting. This
is Python's answer to the Builder pattern, and it's the single highest-value habit in this module.

### Default arguments are evaluated ONCE, at definition time

```python
def append_to(item: str, target: list[str] = []) -> list[str]:  # BUG
    target.append(item)
    return target


append_to("a")  # ['a']
append_to("b")  # ['a', 'b']   <- the same list, still there
```

That `[]` is created once, when the `def` runs, and shared by every call that omits the argument.
It behaves like a Java `static` field, not a local. There is no equivalent trap in Java, and it
*will* bite you once.

The fix:

```python
def append_to(item: str, target: list[str] | None = None) -> list[str]:
    if target is None:
        target = []
    target.append(item)
    return target
```

`ruff` rule `B006` catches this. Mutable defaults: `[]`, `{}`, `set()`, and anything you construct
(`datetime.now()`, `uuid4()`, an object). Immutable defaults (`0`, `""`, `None`, `()`, a frozen
dataclass) are safe.

### Argument forwarding

`*args`/`**kwargs` in a definition *collect*; at a call site they *spread*. That symmetry is what
makes decorators possible:

```python
def wrapper(*args, **kwargs):
    return original(*args, **kwargs)  # forwards anything, unchanged
```

---

## Night 3 — Closures and decorators

**Run:** `examples/04_closures.py`, then `examples/05_decorators.py`

### Closures

An inner function that references an enclosing function's variable keeps that variable alive
after the outer function returns:

```python
def make_counter(start: int = 0) -> Callable[[], int]:
    count = start

    def next_value() -> int:
        nonlocal count  # without this, `count = ...` creates a NEW local
        current = count
        count += 1
        return current

    return next_value
```

`nonlocal` says "assign to the enclosing function's variable." `global` says "assign to the
module-level one" (and is almost always wrong). **Reading** an enclosing variable needs no
keyword; only rebinding does. This is why `count += 1` fails without `nonlocal` but
`items.append(x)` works — the second one mutates, it doesn't rebind.

Java's effectively-final lambda capture is the same idea with the mutation door nailed shut.
Python leaves it open, which is what makes stateful decorators possible.

### Decorators

```python
@my_decorator
def target(): ...
```

is *exactly*:

```python
def target(): ...


target = my_decorator(target)
```

That's the whole feature. No container, no proxy, no bytecode weaving. The canonical shape:

```python
import functools
from collections.abc import Callable
from typing import Any


def count_calls(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)  # copy __name__, __doc__, __wrapped__
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wrapper.call_count += 1  # state on the wrapper object
        return fn(*args, **kwargs)

    wrapper.call_count = 0  # type: ignore[attr-defined]
    return wrapper
```

**Always use `functools.wraps`.** Without it your function's `__name__` becomes `"wrapper"`, its
docstring vanishes, and FastAPI, pytest, and every introspection-based tool downstream breaks.
This is the #1 decorator bug in real codebases.

### Decorator factories (decorators with arguments)

One more layer: a function that returns a decorator.

```python
def retry(attempts: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
    if attempts < 1:  # validate at DECORATION time
        raise ValueError(f"attempts must be >= 1, got {attempts}")

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == attempts:
                        raise
            raise AssertionError("unreachable")

        return wrapper

    return decorator


@retry(3)
def fetch(url: str) -> bytes: ...
```

`@retry(3)` *calls* `retry(3)` first, then applies the returned decorator. Three nested functions
is the standard shape — write it a few times and it stops looking strange.

### Stacking

```python
@count_calls
@retry(3)
def fetch(url: str) -> bytes: ...
```

Applied **bottom-up**: `count_calls(retry(3)(fetch))`. So `retry` is the inner layer, and
`count_calls` counts one call per *logical* invocation, not per retry attempt. Swap the order and
you count attempts instead. Order matters — read decorator stacks inside-out, the same way you
read nested try/finally.

### What this replaces

| Spring | Python |
| --- | --- |
| `@Transactional` | a context manager, or a decorator wrapping one |
| `@Cacheable` | `@functools.cache` / `@functools.lru_cache` |
| `@Retryable` | a `retry` decorator (or `tenacity`) |
| `@Async` | `async def` (Module 07) |
| `@Scheduled` | APScheduler / a cron entry |
| `@Valid` | Pydantic (Module 05) |
| `@Autowired` | a function parameter, or FastAPI `Depends` (Module 09) |
| AOP pointcuts | there is no equivalent, and you won't miss it |

The trade: Python gives you no declarative weaving across a whole codebase. Every decorator is
applied where you can see it. After Spring, that visibility is worth more than the power.

---

## Night 4 — `functools` and friends

**Run:** `examples/06_functools.py`

The stdlib module you should be able to recite:

| Tool | What it does |
| --- | --- |
| `functools.wraps` | metadata-preserving decorator plumbing (non-negotiable) |
| `functools.cache` | unbounded memoization, one line. 3.9+ |
| `functools.lru_cache(maxsize=N)` | bounded memoization with `.cache_info()` / `.cache_clear()` |
| `functools.partial` | pre-bind arguments — `partial(connect, "localhost")` |
| `functools.reduce` | fold. Rarely clearer than a loop; know it, avoid it |
| `functools.singledispatch` | overload by first argument's runtime type |
| `functools.cached_property` | compute once per instance, then cache on it |
| `functools.total_ordering` | derive all comparisons from `__eq__` + `__lt__` |
| `operator.itemgetter` / `attrgetter` | fast, readable sort keys |
| `itertools.chain/groupby/islice/accumulate/pairwise` | lazy sequence tooling |

Two that will change how you write code:

```python
@functools.cache  # memoization. That's it. That's @Cacheable.
def embed(text: str) -> list[float]: ...


from operator import attrgetter, itemgetter

sorted(rows, key=itemgetter(2))  # by index — faster than a lambda
sorted(staff, key=attrgetter("dept", "name"))
```

**Caution on `functools.cache`:** it holds strong references to arguments *and* results forever.
On a method, it keeps every `self` alive — a real memory leak. Use `lru_cache(maxsize=...)` for
anything unbounded, and `cached_property` for per-instance caching.

---

## Exercises

```bash
uv run pytest modules/m02_functions -x -q
```

| File | What it drills |
| --- | --- |
| `exercises/ex01_higher_order.py` | functions as values, closures, `nonlocal`, memoization |
| `exercises/ex02_decorators.py` | `wraps`, decorator factories, class decorators, stacking |

`ex02` is the one that matters. Those nine decorators are, near enough, the ones you'll actually
write in production: retry, cache, trace, deprecate, validate.

When green, compare against `solutions/` — but only then. Read
[solutions/README.md](solutions/README.md) for why.

---

## Weekend — Athena checkpoint 2

Spec: [project/README.md](../../project/README.md) → **Stage 2**.

Refactor Stage 1 with what you learned:

1. Replace your `if fmt == "json" ... elif` output branching with a dispatch table.
2. Make every optional parameter keyword-only.
3. Add `@functools.cache` to the tokenizer and measure the difference on a repeated query.
4. Write one real decorator — `@timed` — that records elapsed time per indexing phase into a
   stats dict, and use it to find your slowest step.
5. Audit for mutable default arguments. Run `uv run ruff check --select B006 .` to confirm.

---

## Self-check — you're done with Week 2 when you can

- [ ] Explain `@dec` as `f = dec(f)` without hesitating
- [ ] Write a `functools.wraps`-correct decorator from memory
- [ ] Write a decorator *factory* from memory (three nested functions)
- [ ] Say what breaks when you forget `wraps`
- [ ] Explain why `def f(x=[])` is a bug and name the ruff rule
- [ ] Say when you need `nonlocal` and when you don't
- [ ] Predict the behaviour of a two-decorator stack in either order
- [ ] Replace a Strategy-pattern class hierarchy with a dict of functions
- [ ] All Module 02 tests green, `ruff` clean

Next: Module 03 — The Data Model (ask for it when you get here)
