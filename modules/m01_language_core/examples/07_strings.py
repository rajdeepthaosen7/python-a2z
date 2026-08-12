"""Strings: f-strings, the methods you'll actually use, and bytes vs str.

Run me:  uv run python modules/m01_language_core/examples/07_strings.py
"""


def main() -> None:
    name, amount, ratio = "Ada", 1234.5678, 0.4267

    # ---- 1. f-strings ----------------------------------------------------
    print("1)", f"{name} owes {amount:.2f}")
    print("2)", f"{amount:>12,.2f}|")  # width 12, right-aligned, thousands
    print("3)", f"{amount:<12,.2f}|{amount:^12.1f}|")  # left / centered
    print("4)", f"{ratio:.1%}")  # 42.7%
    print("5)", f"{255:#x} {255:#b} {255:04d}")  # 0xff 0b11111111 0255
    print("6)", f"{name=} {amount=}")  # self-documenting; debugging gold
    print("7)", f"{name!r} vs {name}")  # !r calls repr() — USE THIS IN ERRORS

    width = 8
    print("8)", f"{name:>{width}}|")  # nested format spec

    # Why !r matters: these two log lines look identical without it.
    for user_id in ("42", 42):
        print(f"9) no such user: {user_id} | with repr: {user_id!r}")

    # ---- 2. Building strings --------------------------------------------
    parts = ["a", "b", "c"]
    print("10)", ", ".join(parts))  # the StringBuilder
    print("11)", "".join(str(n) for n in range(5)))
    # NEVER: s = ""; for p in parts: s += p     (quadratic)

    # Multiline: triple quotes, or implicit adjacent-literal concatenation
    sql = """
        SELECT id, title
        FROM documents
        WHERE corpus = ?
    """
    print("12)", " ".join(sql.split()))

    msg = "this is one long message split across source lines"
    print("13)", msg)

    # ---- 3. The methods worth memorizing --------------------------------
    s = "  Hello, World!  "
    print("14)", repr(s.strip()), repr(s.lstrip()), repr(s.rstrip()))
    print("15)", s.strip().lower(), s.strip().upper(), s.strip().title())
    print("16)", "a,b,,c".split(","), "a b  c".split())  # note: split() collapses
    print("17)", "a,b,c".split(",", maxsplit=1))
    print("18)", "key=value=x".partition("="), "key=value=x".rpartition("="))
    print("19)", "hello".replace("l", "L", 1))
    print("20)", "file.tar.gz".startswith("file"), "file.tar.gz".endswith((".gz", ".zip")))
    print("21)", "hello".find("z"), "hello".index("e"))  # find -> -1, index -> raises
    print("22)", "42".isdigit(), "abc".isalpha(), "a1".isalnum(), "  ".isspace())
    print("23)", "line1\nline2\n".splitlines())
    print("24)", "x".center(7, "-"), "5".zfill(3))
    print("25)", "prefix_body".removeprefix("prefix_"), "body.txt".removesuffix(".txt"))

    # Case-insensitive comparison: casefold, not lower (handles ß, İ, etc.)
    print("26)", "Straße".casefold() == "strasse".casefold())

    # ---- 4. Cleaning text (you'll do this constantly in AI work) --------
    import re
    import string

    raw = "Hello, World! It's 2026 -- ready?"
    no_punct = raw.translate(str.maketrans("", "", string.punctuation))
    print("27)", no_punct)
    print("28)", re.findall(r"[a-z']+", raw.lower()))
    print("29)", re.sub(r"\s+", " ", "a   b\n\tc").strip())

    # ---- 5. str vs bytes -------------------------------------------------
    text = "café"
    data = text.encode("utf-8")  # str -> bytes
    print("30)", data, len(text), len(data))  # 4 chars, 5 bytes
    print("31)", data.decode("utf-8"))

    # Always name the encoding at every boundary — file, socket, subprocess.
    # The platform default differs between your Windows box and the Linux CI runner.
    # with open(path, encoding="utf-8") as f: ...


if __name__ == "__main__":
    main()
