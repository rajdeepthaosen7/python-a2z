"""@dataclass — Lombok and `record`, built in, no annotation processor.

Run me:  uv run python modules/m03_data_model/examples/04_dataclasses.py
"""

import functools
from dataclasses import asdict, dataclass, field, fields, replace
from typing import NamedTuple, TypedDict


# ---- 1. The hand-written version, for comparison ------------------------
class ManualDoc:
    def __init__(self, path: str, title: str) -> None:
        self.path = path
        self.title = title

    def __repr__(self) -> str:
        return f"ManualDoc(path={self.path!r}, title={self.title!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManualDoc):
            return NotImplemented
        return (self.path, self.title) == (other.path, other.title)

    def __hash__(self) -> int:
        return hash((self.path, self.title))


# ---- 2. The same thing, generated ---------------------------------------
@dataclass(frozen=True, slots=True)
class Document:
    """frozen=True  -> read-only + hashable (a Java record)
    slots=True   -> no __dict__, less memory
    """

    path: str
    title: str
    body: str = field(default="", repr=False)  # keep long text out of logs
    tags: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        # Runs after the generated __init__. Your Bean Validation.
        if not self.path:
            raise ValueError("path must not be empty")

    @property
    def word_count(self) -> int:
        # Computed, not stored. NOTE: it must be a plain @property here —
        # functools.cached_property needs a per-instance __dict__ to cache into,
        # and slots=True is precisely what removes that. See Article below.
        return len(self.body.split())


@dataclass(frozen=True)
class Article:
    """Same, without slots, so cached_property works."""

    title: str
    body: str = ""

    @functools.cached_property
    def word_count(self) -> int:
        print("     (computing word_count once)")
        return len(self.body.split())


@dataclass(order=True)
class SearchHit:
    """order=True generates <, <=, >, >= comparing fields IN DECLARATION ORDER."""

    score: float
    path: str
    snippet: str = field(default="", compare=False, repr=False)


@dataclass
class Corpus:
    """Mutable, with the correct mutable default."""

    name: str
    documents: list[Document] = field(default_factory=list)
    _index: dict[str, int] = field(default_factory=dict, repr=False, compare=False)
    version: int = field(init=False, default=1)  # not a constructor parameter


def main() -> None:
    # ---- 3. Generated __init__, __repr__, __eq__, __hash__ ---------------
    doc = Document("a.md", "Alpha", body="one two three", tags=frozenset({"draft"}))
    print("1)", doc)  # body excluded from repr
    print("2)", doc == Document("a.md", "Alpha", "one two three", frozenset({"draft"})))
    print("3)", len({doc, doc}))  # hashable because frozen
    print("4)", doc.word_count)

    # ---- 4. frozen means frozen ------------------------------------------
    try:
        doc.title = "Changed"  # type: ignore[misc]
    except AttributeError as exc:
        print("5)", type(exc).__name__, exc)

    # The frozen "setter" is replace() — it derives a NEW object:
    renamed = replace(doc, title="Alpha v2")
    print("6)", renamed, "| original untouched:", doc.title)

    # ---- 5. __post_init__ validation -------------------------------------
    try:
        Document("", "No path")
    except ValueError as exc:
        print("7)", exc)

    # ---- 6. slots ---------------------------------------------------------
    print("8)", Document.__slots__)
    try:
        doc.typo = 1  # type: ignore[attr-defined]
    except AttributeError as exc:
        print("9)", exc)

    # ---- 7. cached_property ----------------------------------------------
    article = Article("A", "one two three four")
    print("10)", article.word_count, article.word_count)  # computed once

    # ---- 8. order=True and field(compare=False) --------------------------
    hits = [
        SearchHit(0.9, "b.md", snippet="ignored"),
        SearchHit(0.9, "a.md", snippet="also ignored"),
        SearchHit(2.5, "c.md"),
    ]
    print("11) natural (ascending) order:", sorted(hits))
    print("12) best first:", sorted(hits, key=lambda h: (-h.score, h.path)))
    print("13) snippet excluded from ==:", SearchHit(1.0, "x", "p") == SearchHit(1.0, "x", "q"))

    # ---- 9. default_factory — the Module 02 lesson, in dataclass form ----
    c1, c2 = Corpus("first"), Corpus("second")
    c1.documents.append(doc)
    print("14)", len(c1.documents), len(c2.documents))  # 1 0 — independent lists
    print("15)", c1)  # _index hidden from repr; version not a ctor arg

    # `documents: list[Document] = []` would raise at CLASS DEFINITION time.
    # The language learned from the mutable-default footgun and now refuses it.

    # ---- 10. Introspection ------------------------------------------------
    print("16)", [f.name for f in fields(doc)])
    print("17)", {f.name: f.type for f in fields(SearchHit)})
    print("18)", asdict(Corpus("x", [Document("p", "t")]))["documents"][0]["path"])

    # ---- 11. When NOT to use a dataclass ---------------------------------
    class Coord(NamedTuple):  # immutable, indexable, unpackable, tuple-compatible
        x: int
        y: int

    class RowDict(TypedDict):  # just a dict shape, for mypy. No runtime class.
        path: str
        score: float

    point = Coord(1, 2)
    px, py = point
    row: RowDict = {"path": "a.md", "score": 0.5}
    print("19)", point, point[0], px, py, point == (1, 2))
    print("20)", row["path"], type(row).__name__)

    # ---- 12. Dataclasses do NOT validate types ---------------------------
    bogus = Document(path=42, title=None)  # type: ignore[arg-type]
    print("21) no runtime type check:", bogus.path, bogus.title)
    # Annotations are for mypy. Runtime enforcement is Pydantic's job — Module 05.


if __name__ == "__main__":
    main()
