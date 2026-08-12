"""Exceptions, exception chaining, EAFP, and context managers.

Run me:  uv run python modules/m01_language_core/examples/08_exceptions_eafp.py
"""

import contextlib
import tempfile
from pathlib import Path


class AthenaError(Exception):
    """Base class for everything this package raises.

    Give every library ONE base exception so callers can catch your whole
    surface with a single except clause. Java teams do this too; Python teams
    forget because nothing forces them to.
    """


class DocumentNotFoundError(AthenaError):
    def __init__(self, doc_id: str) -> None:
        super().__init__(f"no such document: {doc_id!r}")
        self.doc_id = doc_id  # keep structured data on the exception


def main() -> None:
    # ---- 1. try/except/else/finally --------------------------------------
    def parse_port(raw: str) -> int:
        try:
            port = int(raw)
        except ValueError as exc:
            # `from exc` == initCause(): preserves the original traceback.
            raise AthenaError(f"port must be an integer, got {raw!r}") from exc
        else:
            # Runs only if no exception was raised. Keeps the try block minimal,
            # so you never accidentally catch a ValueError from validation.
            if not 1 <= port <= 65535:
                raise AthenaError(f"port out of range: {port}")
            return port
        finally:
            pass  # cleanup always runs

    print("1)", parse_port("8080"))
    for bad in ("http", "99999"):
        try:
            parse_port(bad)
        except AthenaError as exc:
            print(f"2) {type(exc).__name__}: {exc} (cause={type(exc.__cause__).__name__})")

    # ---- 2. Catch narrowly, in order, and use the tuple form ------------
    def risky(kind: str) -> str:
        match kind:
            case "key":
                return str({"a": 1}["missing"])
            case "index":
                return [][0]
            case "zero":
                return str(1 // 0)
            case _:
                return "ok"

    for kind in ("key", "index", "zero", "fine"):
        try:
            print("3)", kind, risky(kind))
        except (KeyError, IndexError) as exc:  # tuple = multi-catch
            print("3)", kind, "->", type(exc).__name__, repr(exc))
        except ArithmeticError as exc:  # ZeroDivisionError's parent
            print("3)", kind, "->", type(exc).__name__, exc)

    # NEVER `except Exception: pass`. If you truly want to ignore, say so:
    with contextlib.suppress(KeyError):
        _ = {"a": 1}["nope"]
    print("4) suppressed, and a reader can see it was deliberate")

    # ---- 3. Custom exceptions carry data --------------------------------
    try:
        raise DocumentNotFoundError("doc-77")
    except DocumentNotFoundError as exc:
        print("5)", exc, "| structured:", exc.doc_id)

    # ---- 4. LBYL vs EAFP -------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        missing = Path(tmp) / "nope.txt"
        real = Path(tmp) / "yes.txt"
        real.write_text("content", encoding="utf-8")

        # LBYL (the Java instinct): two syscalls, and a race between them.
        if missing.exists():
            print("6)", missing.read_text(encoding="utf-8"))
        else:
            print("6) LBYL: not found")

        # EAFP (idiomatic): one syscall, atomic, faster in the happy path.
        try:
            print("7)", real.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print("7) EAFP: not found")

        # The convenience forms of EAFP you'll use most:
        print("8)", {"a": 1}.get("b", "default"))
        print("9)", getattr(object(), "nope", "default"))
        print("10)", next(iter([]), "empty"))

    # ---- 5. Context managers = try-with-resources ------------------------
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "data.txt"
        with path.open("w", encoding="utf-8") as f:  # always pass encoding
            f.write("line one\nline two\n")

        # Multiple resources, one statement:
        with (
            path.open(encoding="utf-8") as src,
            (Path(tmp) / "copy.txt").open("w", encoding="utf-8") as dst,
        ):
            dst.writelines(line.upper() for line in src)

        print("11)", (Path(tmp) / "copy.txt").read_text(encoding="utf-8").split())

    # Files are closed even if the block raises. Writing your own context
    # managers (__enter__/__exit__, @contextmanager) is Module 03.

    # ---- 6. Read the traceback ------------------------------------------
    try:
        parse_port("nope")
    except AthenaError:
        import traceback

        print("12) full chain:")
        traceback.print_exc()
        # Read tracebacks BOTTOM-UP: last line = what broke,
        # "The above exception was the direct cause" = your `from exc` chain.


if __name__ == "__main__":
    main()
