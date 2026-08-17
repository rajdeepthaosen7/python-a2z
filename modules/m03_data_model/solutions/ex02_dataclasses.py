"""Reference solution — read only after your own version is green."""

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field, fields, replace


@dataclass(frozen=True, slots=True)
class Document:
    path: str
    title: str
    body: str = field(default="", repr=False)
    tags: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.path.strip():
            raise ValueError(f"path must not be empty, got {self.path!r}")

    @property
    def word_count(self) -> int:
        # Plain @property, not cached_property: slots=True removes the
        # per-instance __dict__ that cached_property needs to write into.
        return len(self.body.split())


@dataclass(order=True)
class SearchHit:
    score: float
    path: str
    snippet: str = field(default="", compare=False, repr=False)


@dataclass
class Corpus:
    name: str
    documents: list[Document] = field(default_factory=list)
    version: int = field(init=False, default=1)


def add_tag(document: Document, tag: str) -> Document:
    return replace(document, tags=document.tags | {tag})


def field_names(cls: type) -> list[str]:
    return [f.name for f in fields(cls)]


def to_row(document: Document) -> dict[str, object]:
    data = asdict(document)
    return {
        "path": data["path"],
        "title": data["title"],
        "word_count": document.word_count,  # a property, so not in asdict()
        "tags": sorted(data["tags"]),
    }


def best_hits(hits: Iterable[SearchHit], limit: int) -> list[SearchHit]:
    if limit < 0:
        raise ValueError(f"limit must be non-negative, got {limit}")
    # Not the dataclass's natural order: score descending, path ascending.
    return sorted(hits, key=lambda h: (-h.score, h.path))[:limit]
