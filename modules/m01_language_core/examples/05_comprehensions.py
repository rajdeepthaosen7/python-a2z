"""Comprehensions: your replacement for the Streams API.

Run me:  uv run python modules/m01_language_core/examples/05_comprehensions.py
"""

import sys
from collections.abc import Iterator

WORDS = ["alpha", "beta", "gamma", "delta", "epsilon", "pi"]


def main() -> None:
    # ---- 1. The four forms ----------------------------------------------
    print("1)", [w.upper() for w in WORDS if len(w) > 4])  # list
    print("2)", {len(w) for w in WORDS})  # set
    print("3)", {w: len(w) for w in WORDS if w.startswith("a")})  # dict
    gen = (len(w) for w in WORDS)  # generator (lazy)
    print("4)", type(gen).__name__, sum(gen))

    # Side-by-side with the Java stream you'd have written:
    #   WORDS.stream().filter(w -> w.length() > 4).map(String::toUpperCase).toList()
    # Comprehension order is [ EXPR for VAR in ITER if COND ] — result first.

    # ---- 2. Laziness is the point of generators -------------------------
    squares_list = [n * n for n in range(1_000_000)]
    squares_gen = (n * n for n in range(1_000_000))
    print("5) list bytes:", sys.getsizeof(squares_list), "gen bytes:", sys.getsizeof(squares_gen))

    # Generator expressions passed to a function don't need their own parens:
    print("6)", sum(n * n for n in range(10)), any(w == "pi" for w in WORDS))

    # A generator is single-use. This is the #1 generator bug:
    once = (w for w in WORDS)
    print("7)", list(once), list(once))  # second call is empty!

    # ---- 3. Nested loops read outer-to-inner ----------------------------
    print("8)", [(r, c) for r in "AB" for c in (1, 2)])

    matrix = [[1, 2, 3], [4, 5, 6]]
    print("9)", [cell for row in matrix for cell in row])  # flatten
    print("10)", [[row[i] for row in matrix] for i in range(3)])  # transpose
    print("11)", list(zip(*matrix, strict=True)))  # transpose, better

    # ---- 4. Conditionals: filter vs map ---------------------------------
    nums = [-2, -1, 0, 1, 2]
    print("12)", [n for n in nums if n > 0])  # trailing if  = filter
    print("13)", [n if n > 0 else 0 for n in nums])  # leading if/else = map
    print("14)", [n for n in nums if n > 0 if n % 2 == 1])  # stacked filters

    # ---- 5. The walrus, for compute-once-then-filter --------------------
    def expensive(w: str) -> int:
        return len(w) * 2

    print("15)", [scored for w in WORDS if (scored := expensive(w)) > 8])

    # ---- 6. When NOT to use a comprehension -----------------------------
    # Unreadable — this belongs in a loop or a named function:
    #   [f(x) for xs in data for x in xs if p(x) and q(x) for f in fns]
    #
    # Side effects belong in a loop. A comprehension is for BUILDING a value:
    for w in WORDS:  # right
        if w.startswith("p"):
            print("16)", w)
    # [print(w) for w in WORDS]   # wrong: builds a list of None for no reason

    # ---- 7. Generator functions: lazy pipelines -------------------------
    def read_lines(text: str) -> Iterator[str]:
        for raw in text.splitlines():
            if line := raw.strip():
                yield line

    def parse(lines: Iterator[str]) -> Iterator[tuple[str, int]]:
        for line in lines:
            name, _, value = line.partition("=")
            yield name.strip(), int(value)

    config = "  a = 1 \n\n b = 2\n"
    print("17)", dict(parse(read_lines(config))))
    # Nothing is computed until dict() pulls. This is how you stream a 10 GB
    # file through transformations in constant memory. Module 03 goes deeper.


if __name__ == "__main__":
    main()
