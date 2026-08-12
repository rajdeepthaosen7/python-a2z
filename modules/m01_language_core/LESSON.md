# Module 01 — Language Core (Week 1)

> **Prerequisite:** [SETUP.md](../../SETUP.md) complete.
> **Time:** 4 weeknights × ~1.75h + weekend project checkpoint.
> **Goal:** stop writing Java in Python syntax.

Most Java devs reach "my Python runs" in about three days, and then plateau there for a year
writing `for i in range(len(xs))`. This module is about skipping that year. Every section names
the Java habit and the Python replacement.

---

## Night 1 — Objects, names, and mutability

**Run:** `uv run python modules/m01_language_core/examples/01_names_and_objects.py`

### There are no variables

In Java, `int x = 5` reserves a slot of a declared type and puts a value in it. In Python, `5` is
an object on the heap and `x` is a *name in a namespace* pointing at it. Assignment rebinds the
name; it never copies and never converts.

```python
a = [1, 2, 3]
b = a  # not a copy. Same object, second name.
b.append(4)
print(a)  # [1, 2, 3, 4]
```

If you have ever passed a `List` to a method in Java and been surprised it was modified, this is
the same thing, but it applies to *assignment* too. `id(x)` gives you the identity;
`x is y` compares identity, `x == y` compares value.

**When you need a copy, ask for one:** `b = a.copy()` (shallow) or `copy.deepcopy(a)` (deep).

### Immutable vs mutable is the distinction that matters

| Immutable | Mutable |
| --- | --- |
| `int`, `float`, `bool`, `str`, `bytes`, `tuple`, `frozenset`, `None` | `list`, `dict`, `set`, `bytearray`, most of your own classes |

Immutable objects are hashable, so they can be dict keys and set members. Mutable ones can't
(the same reason you don't mutate a Java object after using it as a `HashMap` key — Python just
refuses outright instead of corrupting your map).

```python
{[1, 2]: "x"}  # TypeError: unhashable type: 'list'
{(1, 2): "x"}  # fine
```

### Everything is truthy or falsy

There is no `boolean` requirement in conditions. These are all falsy:

```python
False  None  0  0.0  ""  []  {}  ()  set()
```

So `if items:` means "if items is non-empty", and it's the idiom. `if len(items) > 0:` is a Java
accent — correct, but it marks you.

The trap: `if x:` is **not** `if x is not None:`. When `0` or `""` is a valid value, be explicit.

```python
def apply_discount(pct: float | None) -> float:
    if pct is None:  # correct: 0.0 is a legitimate discount
        return 1.0
    return 1 - pct
```

### Dynamic typing, static discipline

Python checks types at runtime. Professional Python *annotates* types and checks them with mypy
in CI. Annotations are ignored by the interpreter — they're for tools and humans.

```python
def normalize(text: str, *, lower: bool = True) -> list[str]: ...
```

Rule for this course: **every function you write gets a full annotation.** You already think this
way; don't drop the habit just because the language lets you.

### Practice

- Read `examples/01_names_and_objects.py` and predict each output *before* running it.
- Then run `examples/02_truthiness.py`.

---

## Night 2 — Sequences, slicing, and dicts

**Run:** `examples/03_sequences_and_slicing.py`, then `examples/04_dicts_and_sets.py`

### Indexing and slicing

Negative indices count from the end. Slices are `[start:stop:step]`, `stop` exclusive, and they
never raise for out-of-range bounds.

```python
xs = [0, 1, 2, 3, 4, 5]
xs[-1]  # 5        last element
xs[1:4]  # [1,2,3]
xs[:3]  # [0,1,2]
xs[3:]  # [3,4,5]
xs[::2]  # [0,2,4]  every other
xs[::-1]  # [5,4,3,2,1,0]  reversed copy
xs[100:200]  # []       no IndexOutOfBoundsException
```

Slicing a list gives a **new list** (shallow copy). Slicing a `str` gives a new `str`. This one
feature replaces a large amount of Java loop code — internalize it.

### The sequence toolkit you should reach for

| Instead of a Java loop | Use |
| --- | --- |
| index-based iteration | `for i, x in enumerate(xs):` |
| iterating two lists together | `for a, b in zip(xs, ys):` |
| `Collections.reverse` | `reversed(xs)` |
| `Collections.sort` with Comparator | `sorted(xs, key=..., reverse=True)` |
| `Stream.anyMatch` / `allMatch` | `any(...)` / `all(...)` |
| manual accumulation | `sum`, `min`, `max`, `len` |
| `IntStream.range` | `range(n)` |
| `String.join` | `", ".join(parts)` |
| `String.split` | `text.split(",")` |

`sorted(..., key=fn)` is the single most useful of these. `key` computes a sort value per element,
so `sorted(words, key=len)` and `sorted(people, key=lambda p: (p.dept, -p.salary))` replace
whole `Comparator` chains. Sorting is **stable**, so chained sorts work like `thenComparing`.

### Dicts

```python
counts = {"a": 1, "b": 2}
counts["c"]  # KeyError
counts.get("c")  # None
counts.get("c", 0)  # 0
counts.setdefault("c", 0)  # inserts and returns 0
"c" in counts  # membership tests keys
for k, v in counts.items():
    ...
{**a, **b}  # merge, b wins
a | b  # same thing, 3.9+
```

Two `collections` types remove most counting boilerplate — you'll use both constantly:

```python
from collections import Counter, defaultdict

Counter(words).most_common(3)  # top-3 word counts, one line
groups = defaultdict(list)
for w in words:
    groups[len(w)].append(w)  # no "if key not in map" dance
```

### Practice

Predict, then run, then **break** each example: change an index, remove a `get` default, and read
the traceback. Reading tracebacks fast is a real skill; build it now.

---

## Night 3 — Comprehensions and unpacking

**Run:** `examples/05_comprehensions.py`, then `examples/06_unpacking.py`

### Comprehensions replace Streams

```python
# Java: xs.stream().filter(x -> x > 0).map(x -> x * 2).collect(toList())
[x * 2 for x in xs if x > 0]
```

Read it as: *build a list of `x*2`, for each `x` in `xs`, where `x > 0`.* Four flavors:

```python
[f(x) for x in xs]  # list
{f(x) for x in xs}  # set
{k: f(v) for k, v in d.items()}  # dict
(f(x) for x in xs)  # generator — lazy, single-pass, no memory
```

That last one is the equivalent of a non-collected Stream. `sum(x * x for x in xs)` allocates
nothing.

Nested loops read outer-to-inner, same order as the equivalent `for` statements:

```python
[(r, c) for r in rows for c in cols]
```

**Style limit:** if a comprehension needs more than one `for` plus one `if`, or wraps a line,
write a loop. Cleverness that needs re-reading is not idiomatic — it's just short.

### Unpacking

```python
a, b = 1, 2
a, b = b, a  # swap, no temp
first, *rest = [1, 2, 3, 4]  # first=1, rest=[2,3,4]
*init, last = [1, 2, 3, 4]
(name, age), city = ("Ada", 36), "London"
for k, v in d.items():
    ...  # this is unpacking too
```

Star-unpacking into calls and literals:

```python
def f(a, b, c): ...


args = (1, 2, 3)
f(*args)  # positional spread
kwargs = {"a": 1, "b": 2, "c": 3}
f(**kwargs)  # keyword spread
merged = [*xs, *ys]
```

Multiple return values are just tuples — no `Pair` class, no out-params:

```python
def divmod_like(a: int, b: int) -> tuple[int, int]:
    return a // b, a % b


q, r = divmod_like(17, 5)
```

### `match` — the switch you wish Java had

```python
match event:
    case {"type": "click", "x": x, "y": y}:
        handle_click(x, y)
    case {"type": "key", "code": code} if code < 32:
        handle_control(code)
    case [first, *rest]:
        handle_batch(first, rest)
    case _:
        raise ValueError(f"unknown event: {event!r}")
```

It destructures while it matches. No fallthrough. Use it for shapes of data; use `if/elif` for
simple value equality.

---

## Night 4 — Strings, exceptions, and EAFP

**Run:** `examples/07_strings.py`, then `examples/08_exceptions_eafp.py`

### f-strings

```python
name, amount = "Ada", 1234.5678
f"{name} owes {amount:.2f}"  # 'Ada owes 1234.57'
f"{amount:>12,.2f}"  # right-aligned, thousands separators
f"{name=}"  # "name='Ada'"  — debugging gold
f"{obj!r}"  # calls repr(), what you want in logs and errors
```

Use `!r` in every error message. `f"no such user: {user_id!r}"` tells you whether the id was
`"42"` or `42`; without it you'll debug for an hour.

Never build strings in a loop with `+=`. `"".join(parts)` is the `StringBuilder`.

### Exceptions

No checked exceptions. Nothing declares what it throws. The hierarchy you care about:

```text
BaseException
 └── Exception          <- catch this, or narrower. Never BaseException.
      ├── ValueError        bad value of the right type
      ├── TypeError         wrong type entirely
      ├── KeyError          missing dict key
      ├── IndexError        out-of-range sequence index
      ├── AttributeError    no such attribute
      ├── FileNotFoundError (an OSError)
      └── ...
```

```python
try:
    value = parse(raw)
except ValueError as exc:
    raise ConfigError(f"bad config line: {raw!r}") from exc  # keep the cause
except (KeyError, IndexError):
    ...
else:
    commit(value)  # ran only if no exception
finally:
    cleanup()
```

`raise ... from exc` is `initCause` — it preserves the chain in the traceback. Use it whenever you
translate an exception at a layer boundary.

Custom exceptions are three lines, and worth it:

```python
class AthenaError(Exception):
    """Base for everything this package raises."""


class DocumentNotFound(AthenaError):
    pass
```

Define one package-level base class so callers can catch your library with one `except`.

Never do this:

```python
try:
    risky()
except Exception:
    pass  # silent failure; ruff and every reviewer will flag it
```

### EAFP vs LBYL

**Look Before You Leap** (the Java instinct):

```python
if os.path.exists(path):
    with open(path) as f:  # race condition, and two syscalls
        ...
```

**Easier to Ask Forgiveness than Permission** (the Python idiom):

```python
try:
    with open(path) as f:
        ...
except FileNotFoundError:
    ...
```

EAFP is atomic, faster in the happy path, and idiomatic. Python exceptions don't capture
expensive stack traces the way JVM exceptions do, so they're a normal control-flow tool — not a
last resort. `dict.get`, `getattr(o, name, default)`, and `contextlib.suppress` are the
convenience forms.

### `with` = try-with-resources

```python
with open(path, encoding="utf-8") as f:  # always pass encoding
    data = f.read()
# file is closed here, exception or not
```

Always `encoding="utf-8"`. The platform default differs across machines and will bite you on
Windows specifically.

---

## Exercises

Three files. The docstring is the spec. **Do not open the tests first.**

```bash
uv run pytest modules/m01_language_core -x -q
```

| File | What it drills |
| --- | --- |
| `exercises/ex01_collections.py` | sequences, dicts, comprehensions, sorting with `key` |
| `exercises/ex02_text_stats.py` | strings, `Counter`, normalization, comprehensions |
| `exercises/ex03_log_parser.py` | real parsing: split, unpack, exceptions, aggregation |

`-x` stops at the first failure — work one function at a time. When green:

```bash
uv run ruff check modules/m01_language_core
```

Then reread your solutions and ask: *is there a comprehension, a `key=`, or a `Counter` that
would delete three lines here?* That question, asked every time, is how you become fluent.

---

## Weekend — Athena checkpoint 1

Spec: [project/README.md](../../project/README.md) → **Stage 1**.

Build the stdlib-only document indexer. It should walk a folder, read `.txt`/`.md` files,
normalize their text, build an inverted index, and answer keyword queries ranked by match count.
No dependencies, no classes yet (that's Module 03) — functions, dicts, and lists only.

Constraint that makes it a real exercise: **no `for i in range(len(...))` anywhere**, and every
function annotated and under 20 lines.

---

## Self-check — you're done with Week 1 when you can

- [ ] Explain why `b = a; b.append(1)` changes `a`, and when it doesn't
- [ ] Write `xs[::-1]`, `xs[1:-1]`, `xs[::2]` without thinking
- [ ] Convert any Java stream chain into a comprehension on sight
- [ ] Use `sorted(key=...)` with a tuple key for multi-field sorts
- [ ] Reach for `Counter`/`defaultdict` instead of `if k not in d`
- [ ] Say what `f"{x=}"` and `f"{x!r}"` do and why you want them
- [ ] Explain EAFP to someone else, with an example
- [ ] All Module 01 tests green, `ruff` clean

Next: [Module 02 — Functions & Decorators](../m02_functions/LESSON.md)
