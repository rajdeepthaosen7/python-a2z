"""Dunder methods: how your class gets to behave like a built-in.

Run me:  uv run python modules/m03_data_model/examples/01_dunder_basics.py
"""

from collections.abc import Iterator


class Bare:
    """No dunders. Look at what you get by default."""

    def __init__(self, name: str) -> None:
        self.name = name


class Playlist:
    """The container protocol, implemented by hand."""

    def __init__(self, name: str, tracks: list[str] | None = None) -> None:
        self.name = name
        self.tracks = tracks if tracks is not None else []

    # --- display -----------------------------------------------------------
    def __repr__(self) -> str:
        # Should look like the code that recreates the object.
        return f"Playlist({self.name!r}, {self.tracks!r})"

    def __str__(self) -> str:
        # For humans. If you only write one, write __repr__ — str falls back to it.
        return f"{self.name} ({len(self.tracks)} tracks)"

    def __format__(self, spec: str) -> str:
        if spec == "long":
            return f"{self.name}: " + ", ".join(self.tracks)
        return format(str(self), spec)  # delegate everything else to str

    # --- container ---------------------------------------------------------
    def __len__(self) -> int:
        return len(self.tracks)

    def __getitem__(self, index: int) -> str:
        return self.tracks[index]

    def __setitem__(self, index: int, value: str) -> None:
        self.tracks[index] = value

    def __delitem__(self, index: int) -> None:
        del self.tracks[index]

    def __contains__(self, item: object) -> bool:
        return item in self.tracks

    def __iter__(self) -> Iterator[str]:
        return iter(self.tracks)

    # --- other hooks -------------------------------------------------------
    def __bool__(self) -> bool:
        # Without this, bool() falls back to __len__. Defined here to be explicit.
        return bool(self.tracks)

    def __call__(self, index: int) -> str:
        # Makes instances callable. Rare, but this is how a class can pose as a function.
        return self.tracks[index]


def main() -> None:
    # ---- 1. What you get with no dunders ---------------------------------
    bare = Bare("x")
    print("1)", repr(bare))  # <__main__.Bare object at 0x...> — useless
    print("2)", [Bare("a"), Bare("b")])  # containers print repr of elements

    # ---- 2. repr vs str ---------------------------------------------------
    pl = Playlist("Focus", ["Aja", "Peg", "Deacon Blues"])
    print("3) str: ", str(pl))
    print("4) repr:", repr(pl))
    print("5) print uses str:", pl)
    print("6) but a list uses repr:", [pl])
    # ^ THIS is why __repr__ matters more. You almost always see objects
    #   inside containers, in logs, and in debuggers — all of which use repr.

    print("7)", f"{pl}")  # f-string -> __format__ -> __str__
    print("8)", f"{pl:long}")  # custom format spec
    print("9)", f"{pl:>30}|")  # spec forwarded to str

    # ---- 3. The container protocol ---------------------------------------
    print("10)", len(pl), bool(pl), bool(Playlist("Empty")))
    # Slicing works at RUNTIME because list.__getitem__ accepts a slice — but our
    # annotation says `index: int`, so mypy objects. A fully typed container needs
    # @overload (Module 05) to say "int -> str, slice -> list[str]".
    print("11)", pl[0], pl[-1], pl[1:])  # type: ignore[index]
    print("12)", "Peg" in pl, "Nope" in pl)
    print("13)", [t.upper() for t in pl])  # __iter__ makes comprehensions work

    pl[0] = "Black Cow"
    del pl[2]
    print("14)", pl)

    # Everything below comes free from __iter__ — none of it is code you wrote:
    print("15)", list(pl), sorted(pl), max(pl, key=len))
    first, *rest = pl
    print("16)", first, rest)

    # ---- 4. __call__ ------------------------------------------------------
    print("17)", pl(0), callable(pl))

    # ---- 5. Attribute hooks (know they exist; use them rarely) -----------
    class Loud:
        def __getattr__(self, name: str) -> str:
            # Called ONLY when normal lookup fails. This is how ORMs and mocks
            # fake arbitrary attributes. Powerful, and a debugging nightmare
            # when overused — every typo silently becomes a valid attribute.
            return f"<no attribute {name!r}>"

    loud = Loud()
    print("18)", loud.anything, loud.at_all)

    # ---- 6. Discovering the protocol -------------------------------------
    print("19)", [d for d in dir(pl) if d.startswith("__")][:8])
    print("20)", len.__doc__.splitlines()[0])  # type: ignore[union-attr]


if __name__ == "__main__":
    main()
