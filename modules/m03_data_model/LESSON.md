# Module 03 — The Data Model (Week 3)

> **Prerequisite:** Module 02 tests green.
> **Time:** 4 weeknights × ~1.75h + weekend project checkpoint.
> **Goal:** make your own types behave like built-in ones.

This is the most important module in Phase 1.

Python has no `interface` keyword and no `implements`. Instead it has a published set of
**protocols** — if your class defines `__len__`, then `len(x)` works on it; if it defines
`__iter__`, then `for x in thing` works, and so does `list(thing)`, `sorted(thing)`, unpacking,
and every function in `itertools`. You don't inherit that behaviour. You *opt in* by defining the
method.

The Java instinct is to write `getLength()`, `toStringValue()`, `isEmpty()` and hand people an
API they have to learn. The Python equivalent is to define `__len__` and `__bool__` and hand
people an API they already know. That's the shift this module is about.

---

## Night 1 — Dunder methods

**Run:** `examples/01_dunder_basics.py`, then `examples/02_eq_and_hash.py`

"Dunder" = **d**ouble **under**score, as in `__len__`. They're never called directly — you write
`len(x)` and Python calls `x.__len__()`. Think of them as the operator-overloading hooks Java
mostly doesn't give you.

### The ones you'll write constantly

| You write | Python calls | Java analogue |
| --- | --- | --- |
| `repr(x)`, debugger, REPL | `__repr__` | `toString()` |
| `str(x)`, `print(x)`, f-string | `__str__` | a separate display method |
| `f"{x:>10}"` | `__format__` | `Formattable` |
| `len(x)` | `__len__` | `size()` |
| `if x:` | `__bool__`, else `__len__` | `isEmpty()`, inverted |
| `x in y` | `__contains__`, else `__iter__` | `contains()` |
| `x[k]` | `__getitem__` | `get()` |
| `x[k] = v` | `__setitem__` | `put()` |
| `del x[k]` | `__delitem__` | `remove()` |
| `for i in x` | `__iter__` | `Iterable` |
| `x == y` | `__eq__` | `equals()` |
| `hash(x)` | `__hash__` | `hashCode()` |
| `x < y` | `__lt__` | `Comparable.compareTo` |
| `x + y` | `__add__` | operator overloading (JVM: no) |
| `x()` | `__call__` | `Function.apply` |
| `with x:` | `__enter__` / `__exit__` | `AutoCloseable` |

### `__repr__` is not optional

```python
class Money:
    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"  # unambiguous, for developers

    def __str__(self) -> str:
        return f"{self.amount / 100:.2f} {self.currency}"  # readable, for users
```

The rule: **`__repr__` should look like the code that would recreate the object.** It's what you
see in tracebacks, debuggers, and `print(list_of_objects)` — because containers always use
`repr` on their elements, never `str`. If you write only one, write `__repr__`; `str()` falls
back to it automatically. The reverse is not true.

Without `__repr__` you get `<__main__.Money object at 0x7f3c8a2b1d90>`, which tells you nothing
at 2am.

### Returning `NotImplemented`

Binary dunders take a second operand that might be any type. When you don't know how to handle
it, return the **`NotImplemented` singleton** (not `NotImplementedError`, which is an exception):

```python
def __eq__(self, other: object) -> bool:
    if not isinstance(other, Money):
        return NotImplemented  # "I don't know — ask the other operand"
    return self.amount == other.amount and self.currency == other.currency
```

Python then tries the reflected operation on the right-hand operand (`other.__eq__(self)`), and
only if that also declines does it fall back to a default. For `==` the default is identity, so
`Money(1) == "x"` is `False`. For `<` there is no sensible default, so Python raises `TypeError`
— which is exactly what you want.

This is the single most common mistake in hand-written dunders: raising `TypeError` yourself
instead of returning `NotImplemented`, which breaks the other type's chance to handle it.

### `__eq__` and `__hash__` travel together

Same contract as Java, same trap, enforced more aggressively:

> If `a == b`, then `hash(a) == hash(b)`.

**Defining `__eq__` sets `__hash__` to `None`**, making your class unhashable. Python does this
deliberately: you changed what equality means, so the inherited identity-based hash is now
wrong. You must supply a matching `__hash__`:

```python
def __hash__(self) -> int:
    return hash((self.amount, self.currency))  # hash the same fields __eq__ compares
```

Hashing a tuple of the fields is the idiom — it's `Objects.hash(...)`.

**Only hash immutable state.** If a field can change after the object goes into a `set` or a
`dict`, the object gets lost in the wrong bucket — the same bug as mutating a Java `HashMap` key,
and just as hard to find. Mutable classes should simply stay unhashable; that's the safe default
Python already gives you.

---

## Night 2 — Dataclasses

**Run:** `examples/03_operator_overloading.py`, then `examples/04_dataclasses.py`

Writing `__init__`, `__repr__`, `__eq__` by hand gets old immediately. `@dataclass` generates
them from your annotations. It is Lombok and `record` in one, built into the stdlib, with no
annotation processor and no code generation step you can't read.

```python
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Document:
    path: str
    title: str
    tags: frozenset[str] = frozenset()
    body: str = field(default="", repr=False)
```

That gives you `__init__`, `__repr__`, `__eq__`, and `__hash__` (because `frozen=True`).

### The flags that matter

| Flag | Effect | When |
| --- | --- | --- |
| `frozen=True` | attributes read-only after `__init__`; adds `__hash__` | value objects — your default |
| `slots=True` | no per-instance `__dict__`; less memory, faster attribute access | any class you'll have thousands of |
| `order=True` | generates `__lt__`/`__le__`/`__gt__`/`__ge__` comparing fields **in declaration order**, as a tuple | when a natural ordering exists |
| `kw_only=True` | every field becomes keyword-only | 4+ fields, or same-typed neighbours |
| `eq=False` | keep identity equality | entities with an ID, not value objects |

`frozen=True` ≈ a Java `record`. Mutable `@dataclass` ≈ a Lombok `@Data` bean.

### `field()` for the per-field details

```python
tags: list[str] = field(default_factory=list)  # the Module 02 mutable-default fix
snippet: str = field(default="", compare=False)  # excluded from __eq__ and ordering
_cache: dict = field(default_factory=dict, repr=False, compare=False)
internal: int = field(init=False, default=0)  # not a constructor parameter
```

`default_factory=list` is the same lesson as `def f(x=[])` — a mutable default must be built
fresh per instance. A dataclass refuses to even let you write `tags: list[str] = []`; it raises
at class-definition time. That's the language having learned from the footgun.

### `__post_init__` for validation

```python
@dataclass(frozen=True)
class Document:
    path: str

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("path must not be empty")
```

Runs after the generated `__init__`. This is your Bean Validation, minus the annotations. (On a
`frozen` dataclass you can't assign in `__post_init__` — you'd need
`object.__setattr__(self, "field", value)`. If you find yourself doing that, you probably want a
`@property` instead.)

### The three functions worth knowing

```python
from dataclasses import replace, asdict, fields

replace(doc, title="New")  # a NEW instance with one field changed — the frozen "setter"
asdict(doc)  # recursive dict, for JSON
[f.name for f in fields(doc)]  # introspection, without reflection ceremony
```

`replace()` is how you "modify" a frozen object: you don't, you derive a new one. Same discipline
as Java records with `withX()` methods, generated for free.

### When *not* to use a dataclass

| Need | Use |
| --- | --- |
| immutable, indexable, tuple-like | `NamedTuple` |
| just a dict shape for type-checking | `TypedDict` |
| validation and parsing at a boundary | Pydantic (Module 05) |
| rich behaviour, not just data | a plain class |

Dataclasses do not validate types at runtime. `Document(path=42)` succeeds. Annotations are for
mypy; enforcement is Pydantic's job.

---

## Night 3 — Iterators and generators

**Run:** `examples/05_iterators.py`, then `examples/06_generators.py`

### Iterable vs iterator — the distinction that trips everyone

- **Iterable**: has `__iter__`, which returns a *fresh* iterator each call. A `list` is iterable.
  You can loop over it repeatedly.
- **Iterator**: has `__next__` *and* an `__iter__` that returns `self`. It has a position, and
  it is **consumed as you read it**. A generator is an iterator.

```python
nums = [1, 2, 3]  # iterable
it = iter(nums)  # iterator
next(it)  # 1
next(it)  # 2
list(it)  # [3]   — the first two are gone
list(it)  # []    — exhausted forever
list(nums)  # [1, 2, 3]  — the list itself is fine
```

`for` calls `iter()` on whatever you give it, then `next()` until `StopIteration`. That's the
whole protocol — the same shape as `Iterable`/`Iterator` in Java, except `StopIteration` replaces
`hasNext()`.

**Consequence you will hit for real:** a function taking `Iterable[T]` may only iterate it once,
because the caller might pass a generator. If you need two passes, `items = list(items)` first.
You already met this in Module 01's `summarize()`.

### Generators

A function containing `yield` is a **generator function**. Calling it runs *no code* — it returns
a generator object. Each `next()` runs until the next `yield` and then freezes, keeping all local
state.

```python
def read_records(path: Path) -> Iterator[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        for line in f:  # one line in memory at a time
            if line.strip():
                yield parse(line)
```

That function streams a 10 GB file in constant memory. The `with` block stays open across yields
and closes when the generator is exhausted or garbage-collected.

**`yield from`** delegates to another iterable:

```python
def flatten(nested: Iterable[Iterable[int]]) -> Iterator[int]:
    for inner in nested:
        yield from inner
```

### Pipelines

Generators compose into pipelines where nothing is computed until something pulls:

```python
lines = read_lines(path)  # nothing has happened yet
records = (parse(line) for line in lines)
errors = (r for r in records if r["level"] == "ERROR")
first10 = itertools.islice(errors, 10)
result = list(first10)  # NOW the file is opened and read — and only
# far enough to find 10 errors
```

This is Java's `Stream` laziness, but as ordinary language syntax rather than a library.

### The gotchas

1. **Single use.** Iterating a generator twice gives you nothing the second time.
2. **`len()` doesn't work.** No length without consuming it.
3. **Exceptions surface late** — at the point of consumption, not creation, so tracebacks point
   somewhere surprising.
4. **`return` inside a generator** sets `StopIteration.value`; it does not yield.

---

## Night 4 — Protocols, ABCs, context managers, properties

**Run:** `examples/07_protocols_and_abcs.py`, then `examples/08_context_managers.py`

### Duck typing, made checkable

Python's interfaces are **structural**: a thing is a `Tokenizer` if it has the right method, full
stop. No `implements`, no registration, no import of the interface.

`typing.Protocol` describes that expectation so mypy can verify it, without forcing inheritance:

```python
from typing import Protocol


class Tokenizer(Protocol):
    def tokenize(self, text: str) -> list[str]: ...


def index(doc: str, tokenizer: Tokenizer) -> list[str]:  # mypy checks the shape
    return tokenizer.tokenize(doc)
```

Any class with a matching `tokenize` satisfies this — **including classes written before your
protocol existed**, in libraries you don't control. That's the capability Java interfaces
fundamentally lack, and it's why Protocol is the right default.

### Protocol vs ABC

| | `Protocol` | `abc.ABC` |
| --- | --- | --- |
| Relationship | structural — shape matches | nominal — must inherit |
| Third-party classes | work automatically | must be registered |
| Shared implementation | no | yes |
| Enforced at | type-check time | instantiation time |
| Java analogue | (none — closest is a Go interface) | `abstract class` |

**Default to `Protocol`.** Reach for `ABC` when subclasses genuinely share implementation, or
when you want a hard runtime error on a missing method.

### Context managers

You've used `with` since Module 01. Writing one takes two dunders:

```python
class Timer:
    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self  # this is what `as t` binds

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.elapsed = time.perf_counter() - self.start
        return False  # False = don't suppress the exception
```

`__exit__` receives the exception (or three `None`s). **Returning `True` swallows it** — almost
always wrong, and a silent-failure bug when accidental. Return `False` (or `None`).

The lighter form, for the common case:

```python
from contextlib import contextmanager


@contextmanager
def open_corpus(path: Path) -> Iterator[Corpus]:
    corpus = Corpus.load(path)
    try:
        yield corpus  # everything before = __enter__, after = __exit__
    finally:
        corpus.flush()  # finally, so it runs even when the body raises
```

Exactly one `yield`, always wrapped in `try/finally`. This is your `@Transactional`, except you
can see where it begins and ends.

### Properties

`@property` turns a method into a computed attribute — so you never write a Java-style getter,
and you can add computation later without changing a single caller.

```python
@property
def word_count(self) -> int:
    return len(self.body.split())


doc.word_count  # no parentheses — it's an attribute as far as callers know
```

Start with a plain public attribute. Promote it to a `@property` only when you need computation
or validation. The whole getter/setter-by-default habit is unnecessary here, because converting
later is a non-breaking change.

`@functools.cached_property` computes once per instance and caches — ideal for `word_count` over
a large body.

---

## Exercises

```bash
uv run pytest modules/m03_data_model -x -q
```

| File | What it drills |
| --- | --- |
| `exercises/ex01_dunder.py` | `Money` and `Inventory` — repr, eq/hash, ordering, arithmetic, container protocol |
| `exercises/ex02_dataclasses.py` | frozen/slots/order, `field()`, `__post_init__`, `replace`, properties |
| `exercises/ex03_iterators.py` | generators, laziness, a hand-written iterator, two context managers |

`ex03` has tests that assert **laziness** — that your generator hasn't computed anything before
it's consumed. An eager implementation returning a list will fail even though the values match.
That's deliberate: the point of the module is streaming, not the values.

---

## Weekend — Athena checkpoint 3

Spec: [project/README.md](../../project/README.md) → **Stage 3**.

Replace Stage 2's loose dicts with real types:

1. `@dataclass(frozen=True, slots=True)` for `Document`, `Posting`, and `SearchHit`.
2. A `Corpus` class implementing `__len__`, `__iter__`, `__contains__`, and `__repr__` — so it
   behaves like a built-in collection.
3. Convert ingestion into a **generator pipeline**: `walk → read → tokenize → post`. Prove it
   streams by indexing a large directory and watching memory stay flat.
4. A `@contextmanager` for "open corpus, flush the index on exit, even on exception."
5. Define `Tokenizer` as a `Protocol` and write two implementations (simple split, and your
   Module 01 tokenizer). Swap them without changing the indexer.

The dict-shaped `LogRecord` from Module 01 was training wheels. Feel the difference.

---

## Self-check — you're done with Week 3 when you can

- [ ] Say why `__repr__` matters more than `__str__`, and what containers use
- [ ] Explain when to return `NotImplemented` and why not to raise `TypeError`
- [ ] State the `__eq__`/`__hash__` contract and why defining `__eq__` alone breaks hashing
- [ ] Choose between `@dataclass`, `NamedTuple`, `TypedDict`, and a plain class
- [ ] Explain `default_factory` by reference to the Module 02 mutable-default bug
- [ ] Describe the difference between an iterable and an iterator, with a failure it causes
- [ ] Write a generator pipeline and say exactly when each stage executes
- [ ] Write a context manager both ways, and say what returning `True` from `__exit__` does
- [ ] Argue for `Protocol` over `ABC` — and name the case where `ABC` wins
- [ ] All Module 03 tests green, `ruff` and `mypy` clean

Next: Module 04 — Stdlib & Project Structure
