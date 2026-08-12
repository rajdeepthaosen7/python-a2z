"""Sequences, slicing, and the builtins that replace Java loops.

Run me:  uv run python modules/m01_language_core/examples/03_sequences_and_slicing.py
"""

from dataclasses import dataclass


def main() -> None:
    xs = [0, 1, 2, 3, 4, 5]

    # ---- 1. Indexing ------------------------------------------------------
    print("1)", xs[0], xs[-1], xs[-2])  # 0 5 4

    # ---- 2. Slicing: [start:stop:step], stop exclusive, out-of-range is OK -
    print("2)", xs[1:4], xs[:3], xs[3:], xs[:], xs[100:200])
    print("3)", xs[::2], xs[1::2], xs[::-1], xs[-2:], xs[:-2])

    # A slice produces a NEW list (shallow copy), so this is a safe idiom:
    for x in xs[:]:  # iterate a snapshot while mutating the original
        if x % 2:
            xs.remove(x)
    print("4)", xs)

    # Slice assignment splices in place — no Java equivalent:
    ys = [0, 1, 2, 3, 4]
    ys[1:3] = [9, 9, 9]
    print("5)", ys)
    del ys[0:2]
    print("6)", ys)

    # ---- 3. Iteration builtins --------------------------------------------
    words = ["alpha", "beta", "gamma"]

    for i, w in enumerate(words, start=1):  # never `range(len(...))`
        print(f"7) {i}. {w}")

    sizes = [5, 4, 5]
    for w, n in zip(words, sizes, strict=True):  # strict= catches length bugs
        print(f"8) {w} has {n} chars")

    print("9)", list(reversed(words)))
    print("10)", any(w.startswith("b") for w in words))
    print("11)", all(len(w) >= 4 for w in words))
    print("12)", sum(sizes), min(sizes), max(sizes), len(sizes))
    print("13)", max(words, key=len))  # max BY a computed key

    # ---- 4. sorted(key=...) replaces Comparator chains --------------------
    @dataclass
    class Employee:
        name: str
        dept: str
        salary: int

    staff = [
        Employee("ada", "eng", 120),
        Employee("bob", "ops", 90),
        Employee("cy", "eng", 150),
        Employee("dee", "ops", 90),
    ]

    # Java: comparing(Employee::dept).thenComparing(reverseOrder(), ::salary)
    ranked = sorted(staff, key=lambda e: (e.dept, -e.salary))
    print("14)", [(e.dept, e.salary, e.name) for e in ranked])

    # Sorting is STABLE, so successive sorts compose like thenComparing:
    by_name = sorted(staff, key=lambda e: e.name)
    by_salary_then_name = sorted(by_name, key=lambda e: e.salary)
    print("15)", [(e.salary, e.name) for e in by_salary_then_name])

    # ---- 5. Strings are sequences too ------------------------------------
    s = "python"
    print("16)", s[0], s[-1], s[2:4], s[::-1], len(s))
    print("17)", "-".join(sorted(set("mississippi"))))

    # ---- 6. Tuples: fixed-shape records ----------------------------------
    point = (3, 4)
    x, y = point  # unpack
    print("18)", x, y, point + (5,))  # tuples are immutable: + makes a new one

    # A one-element tuple needs the trailing comma. This bites everyone once.
    print("19)", type((1,)).__name__, type((1)).__name__)


if __name__ == "__main__":
    main()
