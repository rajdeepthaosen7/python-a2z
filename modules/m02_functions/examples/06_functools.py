"""functools, operator, itertools: the batteries you should stop reimplementing.

Run me:  uv run python modules/m02_functions/examples/06_functools.py
"""

import functools
import itertools
import operator
import time


def main() -> None:
    # ---- 1. cache / lru_cache = @Cacheable -------------------------------
    call_count = 0

    @functools.cache
    def slow_square(n: int) -> int:
        nonlocal call_count
        call_count += 1
        time.sleep(0.01)
        return n * n

    print("1)", [slow_square(n) for n in (2, 3, 2, 3, 2)], "actual calls:", call_count)
    print("2)", slow_square.cache_info())
    slow_square.cache_clear()
    print("3)", slow_square.cache_info())

    # Bounded variant — use this for anything with unbounded key space:
    @functools.lru_cache(maxsize=2)
    def bounded(n: int) -> int:
        return n

    for n in (1, 2, 3, 1):
        bounded(n)
    print("4)", bounded.cache_info())  # note the eviction

    # WARNING: functools.cache holds strong refs to args and results forever.
    # On a method it keeps every `self` alive -> memory leak. For per-instance
    # caching use cached_property:
    class Corpus:
        def __init__(self, docs: list[str]) -> None:
            self.docs = docs

        @functools.cached_property
        def vocabulary(self) -> set[str]:
            print("     (computing vocabulary once)")
            return {w for d in self.docs for w in d.split()}

    corpus = Corpus(["a b", "b c"])
    print("5)", corpus.vocabulary, corpus.vocabulary)  # computed once

    # ---- 2. partial: pre-bind arguments ---------------------------------
    def connect(host: str, port: int, *, timeout: float = 5.0) -> str:
        return f"{host}:{port} t={timeout}"

    local = functools.partial(connect, "localhost")
    local_fast = functools.partial(connect, "localhost", timeout=0.1)
    print("6)", local(5432), local_fast(6379))
    print("7)", local.func.__name__, local.args, local_fast.keywords)

    # Common real use: adapting a function to a callback signature.
    print("8)", sorted(["b", "A", "c"], key=functools.partial(str.lower)))

    # ---- 3. reduce: know it, then prefer a loop or sum() ----------------
    print("9)", functools.reduce(operator.mul, [1, 2, 3, 4]))  # 24
    print("10)", functools.reduce(operator.or_, [{1}, {2}, {2, 3}]))
    print("11)", sum([1, 2, 3, 4]), math_prod([1, 2, 3, 4]))
    # If sum/min/max/any/all/math.prod covers it, use those instead.

    # ---- 4. singledispatch: overload on the first arg's runtime type ----
    @functools.singledispatch
    def describe(value: object) -> str:
        return f"unknown: {value!r}"

    @describe.register
    def _(value: int) -> str:
        return f"int {value}"

    @describe.register
    def _(value: str) -> str:
        return f"str of length {len(value)}"

    @describe.register(list)
    def _(value: list) -> str:  # type: ignore[type-arg]
        return f"list of {len(value)}"

    for v in (7, "hello", [1, 2], 3.5):
        print("12)", describe(v))
    # This is Java's method overloading, resolved at RUNTIME on the first arg.
    # Useful for serializers and renderers; usually a Protocol is better design.

    # ---- 5. total_ordering ----------------------------------------------
    @functools.total_ordering
    class Version:
        def __init__(self, text: str) -> None:
            self.parts = tuple(int(p) for p in text.split("."))

        def __eq__(self, other: object) -> bool:
            return isinstance(other, Version) and self.parts == other.parts

        def __lt__(self, other: "Version") -> bool:
            return self.parts < other.parts

        def __hash__(self) -> int:
            return hash(self.parts)

        def __repr__(self) -> str:
            return f"Version({'.'.join(map(str, self.parts))!r})"

    versions = [Version("1.10.0"), Version("1.2.0"), Version("2.0.0")]
    print("13)", sorted(versions), Version("1.2.0") <= Version("1.10.0"))
    # total_ordering derived <=, >, >= from just __eq__ and __lt__.

    # ---- 6. operator: fast, readable keys -------------------------------
    rows = [("ada", "eng", 120), ("bob", "ops", 90), ("cy", "eng", 150)]
    print("14)", sorted(rows, key=operator.itemgetter(1, 2)))
    print("15)", list(map(operator.itemgetter(0), rows)))

    # ---- 7. itertools: the lazy toolkit ---------------------------------
    print("16)", list(itertools.chain([1, 2], [3], [4, 5])))
    print("17)", list(itertools.islice(itertools.count(10), 4)))  # 10,11,12,13
    print("18)", list(itertools.accumulate([1, 2, 3, 4])))
    print("19)", list(itertools.pairwise([1, 2, 3, 4])))  # sliding window, 3.10+
    print("20)", list(itertools.product("ab", [1, 2])))
    print("21)", list(itertools.combinations("abc", 2)))
    print("22)", [k for k, _ in itertools.groupby("aaabbbcca")])
    print("23)", list(itertools.takewhile(lambda x: x < 3, [1, 2, 3, 1])))
    print("24)", list(itertools.zip_longest("ab", [1, 2, 3], fillvalue="-")))

    # groupby REQUIRES sorted input — the #1 itertools bug:
    staff = sorted(rows, key=operator.itemgetter(1))
    for dept, group in itertools.groupby(staff, key=operator.itemgetter(1)):
        print("25)", dept, [g[0] for g in group])

    # ---- 8. What to reach for, in order ---------------------------------
    # 1. a builtin (sum, sorted, any, min, max, zip, enumerate)
    # 2. a comprehension
    # 3. itertools / functools / operator / collections
    # 4. a third-party dependency
    # 5. your own implementation
    # Most Java devs start at 5. Working backwards from 1 is the whole skill.


def math_prod(values: list[int]) -> int:
    import math

    return math.prod(values)


if __name__ == "__main__":
    main()
