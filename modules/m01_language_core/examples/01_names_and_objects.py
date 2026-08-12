"""Names bind to objects; assignment never copies.

Run me:  uv run python modules/m01_language_core/examples/01_names_and_objects.py

Predict every printed value BEFORE you run this. The ones you get wrong are the
Java habits you need to unlearn.
"""


def main() -> None:
    # ---- 1. Assignment binds a name, it does not copy -----------------------
    a = [1, 2, 3]
    b = a
    b.append(4)
    print("1)", a, b, a is b)  # both changed; same object

    c = a.copy()  # shallow copy
    c.append(5)
    print("2)", a, c, a is c)

    # ---- 2. Rebinding vs mutating ------------------------------------------
    x = [1, 2]
    y = x
    x = [9, 9]  # REBINDS x. y still points at the original.
    print("3)", x, y)

    x = [1, 2]
    y = x
    x += [9]  # MUTATES in place for lists (list.__iadd__ == extend)
    print("4)", x, y)

    n = 1
    m = n
    n += 1  # ints are immutable: this rebinds n to a NEW int
    print("5)", n, m)

    # ---- 3. Function arguments are passed by object reference ---------------
    def try_to_replace(items: list[int]) -> None:
        items = [99]  # rebinds the local name only
        items.append(100)

    def actually_mutate(items: list[int]) -> None:
        items.append(99)  # visible to the caller

    data = [1]
    try_to_replace(data)
    print("6)", data)
    actually_mutate(data)
    print("7)", data)

    # ---- 4. The identity trap ---------------------------------------------
    p = 256
    q = 256
    print("8)", p is q)  # True: small ints are interned (an implementation detail)

    p = 257
    q = 257
    print("9)", p is q)  # may be False. NEVER use `is` for value comparison.

    s1 = "hello world"
    s2 = "hello" + " world"
    print("10)", s1 == s2, s1 is s2)  # equal in value; identity is not guaranteed

    # Rule: `is` is for None, True, False, and sentinels. `==` for everything else.
    value: str | None = None
    print("11)", value is None)

    # ---- 5. Shallow copies are shallow -------------------------------------
    grid = [[0, 0], [0, 0]]
    shallow = grid.copy()
    shallow[0][0] = 7  # inner lists are shared!
    print("12)", grid)

    import copy

    deep = copy.deepcopy(grid)
    deep[0][0] = 42
    print("13)", grid, deep)

    # ---- 6. The mutable-class-attribute bug (Java's `static` field) --------
    class Registry:
        entries: list[str] = []  # shared by ALL instances — almost always a bug

        def add(self, name: str) -> None:
            self.entries.append(name)

    r1, r2 = Registry(), Registry()
    r1.add("a")
    print("14)", r2.entries)  # ['a'] — surprise. Module 03 shows the fix.


if __name__ == "__main__":
    main()
