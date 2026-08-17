"""Exercise 02 — dataclasses: frozen, slots, order, field(), __post_init__.

These are the Athena domain types you'll actually use from Stage 3 onward.

Run:  uv run pytest modules/m03_data_model/tests/test_ex02_dataclasses.py -x -q

Constraints:
  * Use @dataclass. Do not hand-write __init__, __repr__, __eq__ or __hash__.
  * Use `field()` where the spec calls for a factory, exclusion, or repr change.
  * `replace`, `asdict` and `fields` come from `dataclasses` — use them rather
    than reimplementing.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field, fields, replace  # noqa: F401  (you'll need these)


@dataclass
class Document:
    """An indexed document.

    Required behaviour:
      * frozen (read-only after construction) and therefore hashable
      * uses __slots__
      * fields, in this order:
            path: str
            title: str
            body: str          default "",  EXCLUDED from repr
            tags: frozenset[str]  default empty frozenset
      * __post_init__ raises ValueError if `path` is empty or whitespace-only
      * a `word_count` property returning len(body.split())

    Why a plain @property and not functools.cached_property: cached_property
    needs a per-instance __dict__ to write into, and slots=True is exactly
    what removes it. Try it if you want to see the error.

        >>> doc = Document("a.md", "Alpha", "one two three")
        >>> doc.word_count
        3
        >>> repr(doc)
        "Document(path='a.md', title='Alpha', tags=frozenset())"
    """


@dataclass
class SearchHit:
    """One ranked search result.

    Required behaviour:
      * ordered — <, <=, >, >= generated, comparing fields in declaration order
      * fields, in this order:
            score: float
            path: str
            snippet: str   default "", EXCLUDED from both comparison and repr

    So two hits with the same score and path are equal even if their snippets
    differ, and `sorted(hits)` gives ascending score, then ascending path.
    """


@dataclass
class Corpus:
    """A mutable collection of documents.

    Required behaviour:
      * NOT frozen
      * fields:
            name: str
            documents: list[Document]   default: a NEW empty list per instance
            version: int                always 1, NOT a constructor parameter

    `documents` is the Module 02 mutable-default lesson in dataclass form: a
    bare `= []` raises at class-definition time, so you must say how to build
    a fresh one. `version` is set without being accepted from the caller.
    """


def add_tag(document: Document, tag: str) -> Document:
    """Return a NEW Document with `tag` added to its tags.

    The input must not be modified (it cannot be — it's frozen). If the tag is
    already present, the result still compares equal to the input.

    >>> add_tag(Document("a.md", "A"), "draft").tags
    frozenset({'draft'})

    Hint: dataclasses.replace is the frozen "setter".
    """
    raise NotImplementedError


def field_names(cls: type) -> list[str]:
    """Return the declared field names of a dataclass, in declaration order.

    >>> field_names(SearchHit)
    ['score', 'path', 'snippet']

    Hint: dataclasses.fields. This is introspection without reflection ceremony.
    """
    raise NotImplementedError


def to_row(document: Document) -> dict[str, object]:
    """Flatten a Document into a JSON-ready dict.

    Keys exactly: "path", "title", "word_count", "tags".
    "tags" must be a SORTED list of strings (a frozenset is not JSON-serializable).
    "word_count" comes from the property, so it is NOT one of the dataclass fields.

    >>> to_row(Document("a.md", "A", "x y", frozenset({"b", "a"})))
    {'path': 'a.md', 'title': 'A', 'word_count': 2, 'tags': ['a', 'b']}
    """
    raise NotImplementedError


def best_hits(hits: Iterable[SearchHit], limit: int) -> list[SearchHit]:
    """Return the `limit` best hits: score DESCENDING, then path ASCENDING.

    Note this is deliberately NOT the dataclass's natural order — `sorted(hits)`
    would give ascending score, and `reverse=True` would also reverse the path
    tie-break. You need an explicit key. (Module 01 taught you the tuple trick.)

    Raises:
        ValueError: if limit is negative.
    """
    raise NotImplementedError
