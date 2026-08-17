"""Generators: lazy pipelines, in language syntax rather than a Stream library.

Run me:  uv run python modules/m03_data_model/examples/06_generators.py
"""

import itertools
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path


def counted(label: str, values: Iterator[int]) -> Iterator[int]:
    """Wraps a stream and prints as each element passes — so you can SEE laziness."""
    for value in values:
        print(f"     [{label}] pulled {value}")
        yield value


def read_lines(path: Path) -> Iterator[str]:
    """Streams a file. One line in memory at a time, whatever the file size."""
    print("     (opening file)")
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if stripped := line.strip():
                yield stripped
    print("     (file closed)")


def flatten(nested: Iterator[list[int]]) -> Iterator[int]:
    for inner in nested:
        yield from inner  # delegate to another iterable


def fibonacci() -> Iterator[int]:
    """Infinite. Perfectly safe, because nothing is computed until pulled."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def with_return() -> Iterator[int]:
    yield 1
    yield 2
    return "done"  # type: ignore[return-value]  # sets StopIteration.value; does NOT yield


def main() -> None:
    # ---- 1. Calling a generator function runs NO code ---------------------
    gen = counted("demo", iter([1, 2, 3]))
    print("1)", type(gen).__name__, "— nothing printed above, nothing ran yet")
    print("2)", next(gen))  # NOW the first element is produced
    print("3)", list(gen))  # and the rest

    # ---- 2. Memory ---------------------------------------------------------
    as_list = [n * n for n in range(1_000_000)]
    as_gen = (n * n for n in range(1_000_000))
    print("4) list:", sys.getsizeof(as_list), "bytes | generator:", sys.getsizeof(as_gen))
    print("5)", sum(n * n for n in range(1000)))  # no intermediate list at all

    # ---- 3. A pipeline: nothing runs until something pulls ---------------
    print("6) building the pipeline...")
    stage1 = counted("stage1", iter(range(10)))
    stage2 = (n * 10 for n in stage1)
    stage3 = (n for n in stage2 if n % 20 == 0)
    print("7) ...built. No output above, because nothing has pulled yet.")
    print("8) taking 2:", list(itertools.islice(stage3, 2)))
    # Look at the [stage1] lines: it pulled only as far as it had to.
    # That is Java Stream laziness, without the Stream API.

    # ---- 4. Infinite streams ----------------------------------------------
    print("9)", list(itertools.islice(fibonacci(), 10)))
    print("10)", next(n for n in fibonacci() if n > 1000))  # first match, then stop

    # ---- 5. yield from -----------------------------------------------------
    print("11)", list(flatten(iter([[1, 2], [], [3, 4]]))))

    # ---- 6. Streaming a file -----------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "log.txt"
        path.write_text("alpha\n\nbeta\ngamma\n", encoding="utf-8")

        print("12) creating the generator:")
        lines = read_lines(path)  # file NOT opened yet
        print("13) consuming it:")
        print("14)", list(lines))
        # Note the open/close messages appear during consumption, not creation.
        # The `with` block stays open ACROSS yields and closes on exhaustion.

    # ---- 7. The gotchas ----------------------------------------------------
    once = (n for n in range(3))
    print("15)", list(once), list(once))  # second is empty — single use

    try:
        len(n for n in range(3))  # type: ignore[arg-type]
    except TypeError as exc:
        print("16)", exc)  # no len() without consuming

    gen2 = with_return()
    print("17)", list(gen2))  # [1, 2] — the return value is not yielded
    gen3 = with_return()
    next(gen3), next(gen3)
    try:
        next(gen3)
    except StopIteration as stop:
        print("18) StopIteration.value =", stop.value)

    # Exceptions surface at CONSUMPTION time, not creation time:
    def explodes() -> Iterator[int]:
        yield 1
        raise ValueError("boom")

    boom = explodes()  # no error here
    print("19)", next(boom))
    try:
        next(boom)
    except ValueError as exc:
        print("20) raised only when pulled:", exc)

    # ---- 8. Generator expression vs comprehension -------------------------
    print("21)", [n for n in range(5)])  # list  — eager, reusable, has len()
    print("22)", (n for n in range(5)))  # genexp — lazy, single use, no len()
    print("23)", sum(n for n in range(5)))  # parens optional as a sole argument


if __name__ == "__main__":
    main()
