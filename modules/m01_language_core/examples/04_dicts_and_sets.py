"""Dicts, sets, and the `collections` types that delete boilerplate.

Run me:  uv run python modules/m01_language_core/examples/04_dicts_and_sets.py
"""

from collections import Counter, defaultdict

LOG = """INFO auth ok
ERROR auth token expired
INFO search ok
ERROR db timeout
ERROR auth bad password
WARN search slow"""


def main() -> None:
    # ---- 1. Access patterns ----------------------------------------------
    d = {"a": 1, "b": 2}
    print("1)", d["a"], d.get("z"), d.get("z", 0))
    print("2)", "a" in d, list(d), list(d.values()), list(d.items()))

    # Dicts preserve insertion order (guaranteed since 3.7).
    ordered = {"z": 1, "a": 2, "m": 3}
    print("3)", list(ordered))

    # setdefault: get-or-insert in one call
    index: dict[str, list[int]] = {}
    for pos, ch in enumerate("banana"):
        index.setdefault(ch, []).append(pos)
    print("4)", index)

    # ---- 2. defaultdict: no "if key not in map" dance --------------------
    groups: defaultdict[int, list[str]] = defaultdict(list)
    for word in ["hi", "bye", "yo", "hello"]:
        groups[len(word)].append(word)
    print("5)", dict(groups))

    tallies: defaultdict[str, int] = defaultdict(int)
    for line in LOG.splitlines():
        tallies[line.split()[0]] += 1
    print("6)", dict(tallies))

    # ---- 3. Counter: the whole point of this section ---------------------
    levels = Counter(line.split()[0] for line in LOG.splitlines())
    print("7)", levels)
    print("8)", levels.most_common(2), levels["ERROR"], levels["NOPE"])  # missing -> 0

    services = Counter(line.split()[1] for line in LOG.splitlines())
    print("9)", services.total(), services.most_common())

    # Counters do arithmetic:
    print("10)", Counter("aab") + Counter("abc"), Counter("aab") - Counter("abc"))

    # ---- 4. Merging and transforming ------------------------------------
    defaults = {"host": "localhost", "port": 5432, "ssl": False}
    override = {"port": 6543}
    print("11)", defaults | override)  # 3.9+; right side wins
    print("12)", {**defaults, **override})  # same, older syntax

    upper = {k.upper(): v for k, v in defaults.items()}
    print("13)", upper)

    inverted = {v: k for k, v in {"a": 1, "b": 2}.items()}
    print("14)", inverted)  # careful: duplicate values collapse

    # ---- 5. Sets: membership and algebra --------------------------------
    a = {1, 2, 3, 4}
    b = {3, 4, 5}
    print("15)", a & b, a | b, a - b, a ^ b)
    print("16)", a.issubset({1, 2, 3, 4, 5}), a.isdisjoint({9}))

    # Deduplicate while preserving order — dict keys are an ordered set:
    dupes = ["b", "a", "b", "c", "a"]
    print("17)", list(dict.fromkeys(dupes)))
    print("18)", sorted(set(dupes)))  # dedupe, order lost then re-sorted

    # ---- 6. Keys must be hashable ---------------------------------------
    try:
        {["nope"]: 1}
    except TypeError as exc:
        print("19)", type(exc).__name__, exc)

    print("20)", {(1, 2): "point", frozenset({1, 2}): "pair"})


if __name__ == "__main__":
    main()
