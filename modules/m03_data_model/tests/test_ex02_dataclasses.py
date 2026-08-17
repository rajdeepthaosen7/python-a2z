"""Grader for ex02_dataclasses."""

import dataclasses

import pytest

from modules.m03_data_model.exercises.ex02_dataclasses import (
    Corpus,
    Document,
    SearchHit,
    add_tag,
    best_hits,
    field_names,
    to_row,
)


class TestDocument:
    def test_is_a_dataclass(self) -> None:
        assert dataclasses.is_dataclass(Document)

    def test_construction_and_defaults(self) -> None:
        doc = Document("a.md", "Alpha")
        assert (doc.path, doc.title, doc.body, doc.tags) == ("a.md", "Alpha", "", frozenset())

    def test_field_order(self) -> None:
        assert [f.name for f in dataclasses.fields(Document)] == ["path", "title", "body", "tags"]

    def test_generated_equality(self) -> None:
        assert Document("a.md", "A", "body") == Document("a.md", "A", "body")
        assert Document("a.md", "A") != Document("b.md", "A")

    def test_is_frozen(self) -> None:
        doc = Document("a.md", "A")
        with pytest.raises(dataclasses.FrozenInstanceError):
            doc.title = "Changed"

    def test_is_hashable_because_frozen(self) -> None:
        assert len({Document("a.md", "A"), Document("a.md", "A")}) == 1

    def test_uses_slots(self) -> None:
        assert hasattr(Document, "__slots__")
        with pytest.raises(AttributeError):
            Document("a.md", "A").typo = 1

    def test_body_excluded_from_repr(self) -> None:
        rendered = repr(Document("a.md", "Alpha", "secret body text"))
        assert "secret body text" not in rendered
        assert "a.md" in rendered and "Alpha" in rendered

    @pytest.mark.parametrize("bad", ["", "   ", "\t"])
    def test_empty_path_raises(self, bad: str) -> None:
        with pytest.raises(ValueError):
            Document(bad, "A")

    def test_word_count_property(self) -> None:
        assert Document("a.md", "A", "one two three").word_count == 3

    def test_word_count_empty_body(self) -> None:
        assert Document("a.md", "A").word_count == 0

    def test_word_count_is_a_property_not_a_field(self) -> None:
        assert isinstance(Document.__dict__["word_count"], property)
        assert "word_count" not in [f.name for f in dataclasses.fields(Document)]


class TestSearchHit:
    def test_is_a_dataclass(self) -> None:
        assert dataclasses.is_dataclass(SearchHit)

    def test_field_order(self) -> None:
        assert [f.name for f in dataclasses.fields(SearchHit)] == ["score", "path", "snippet"]

    def test_snippet_defaults_to_empty(self) -> None:
        assert SearchHit(1.0, "a.md").snippet == ""

    def test_snippet_excluded_from_equality(self) -> None:
        assert SearchHit(1.0, "a.md", "one") == SearchHit(1.0, "a.md", "two")

    def test_snippet_excluded_from_repr(self) -> None:
        assert "hidden" not in repr(SearchHit(1.0, "a.md", "hidden"))

    def test_natural_order_is_ascending_by_score_then_path(self) -> None:
        hits = [SearchHit(2.0, "b.md"), SearchHit(1.0, "z.md"), SearchHit(2.0, "a.md")]
        assert [(h.score, h.path) for h in sorted(hits)] == [
            (1.0, "z.md"),
            (2.0, "a.md"),
            (2.0, "b.md"),
        ]

    def test_comparison_operators_exist(self) -> None:
        assert SearchHit(1.0, "a") < SearchHit(2.0, "a")
        assert SearchHit(2.0, "a") >= SearchHit(2.0, "a")


class TestCorpus:
    def test_is_a_dataclass(self) -> None:
        assert dataclasses.is_dataclass(Corpus)

    def test_is_mutable(self) -> None:
        corpus = Corpus("docs")
        corpus.name = "renamed"
        assert corpus.name == "renamed"

    def test_documents_defaults_to_empty_list(self) -> None:
        assert Corpus("docs").documents == []

    def test_each_instance_gets_its_own_list(self) -> None:
        """The Module 02 mutable-default lesson, in dataclass form."""
        first, second = Corpus("a"), Corpus("b")
        first.documents.append(Document("x.md", "X"))
        assert len(first.documents) == 1
        assert len(second.documents) == 0

    def test_version_is_one(self) -> None:
        assert Corpus("docs").version == 1

    def test_version_is_not_a_constructor_argument(self) -> None:
        version = next(f for f in dataclasses.fields(Corpus) if f.name == "version")
        assert version.init is False
        with pytest.raises(TypeError):
            Corpus("docs", [], 5)

    def test_accepts_documents(self) -> None:
        doc = Document("a.md", "A")
        assert Corpus("docs", [doc]).documents == [doc]


class TestAddTag:
    def test_adds_a_tag(self) -> None:
        assert add_tag(Document("a.md", "A"), "draft").tags == frozenset({"draft"})

    def test_keeps_existing_tags(self) -> None:
        doc = Document("a.md", "A", "", frozenset({"old"}))
        assert add_tag(doc, "new").tags == frozenset({"old", "new"})

    def test_returns_a_new_object(self) -> None:
        doc = Document("a.md", "A")
        result = add_tag(doc, "draft")
        assert result is not doc
        assert doc.tags == frozenset()

    def test_other_fields_are_preserved(self) -> None:
        doc = Document("a.md", "Alpha", "body text")
        tagged = add_tag(doc, "draft")
        assert (tagged.path, tagged.title, tagged.body) == ("a.md", "Alpha", "body text")

    def test_duplicate_tag_is_idempotent(self) -> None:
        doc = Document("a.md", "A", "", frozenset({"draft"}))
        assert add_tag(doc, "draft") == doc


class TestFieldNames:
    def test_search_hit(self) -> None:
        assert field_names(SearchHit) == ["score", "path", "snippet"]

    def test_document(self) -> None:
        assert field_names(Document) == ["path", "title", "body", "tags"]

    def test_corpus_includes_non_init_fields(self) -> None:
        assert field_names(Corpus) == ["name", "documents", "version"]


class TestToRow:
    def test_shape(self) -> None:
        doc = Document("a.md", "A", "x y", frozenset({"b", "a"}))
        assert to_row(doc) == {"path": "a.md", "title": "A", "word_count": 2, "tags": ["a", "b"]}

    def test_tags_are_a_sorted_list(self) -> None:
        doc = Document("a.md", "A", "", frozenset({"z", "m", "a"}))
        assert to_row(doc)["tags"] == ["a", "m", "z"]

    def test_no_tags(self) -> None:
        assert to_row(Document("a.md", "A"))["tags"] == []

    def test_body_is_not_included(self) -> None:
        assert "body" not in to_row(Document("a.md", "A", "secret"))


class TestBestHits:
    def test_score_descending(self) -> None:
        hits = [SearchHit(1.0, "a.md"), SearchHit(3.0, "b.md"), SearchHit(2.0, "c.md")]
        assert [h.path for h in best_hits(hits, 3)] == ["b.md", "c.md", "a.md"]

    def test_ties_broken_by_path_ascending(self) -> None:
        hits = [SearchHit(1.0, "z.md"), SearchHit(1.0, "a.md")]
        assert [h.path for h in best_hits(hits, 2)] == ["a.md", "z.md"]

    def test_limit_truncates(self) -> None:
        hits = [SearchHit(float(n), f"{n}.md") for n in range(5)]
        assert len(best_hits(hits, 2)) == 2

    def test_limit_larger_than_input(self) -> None:
        assert len(best_hits([SearchHit(1.0, "a.md")], 99)) == 1

    def test_limit_zero(self) -> None:
        assert best_hits([SearchHit(1.0, "a.md")], 0) == []

    def test_negative_limit_raises(self) -> None:
        with pytest.raises(ValueError):
            best_hits([], -1)

    def test_accepts_any_iterable(self) -> None:
        hits = (SearchHit(float(n), f"{n}.md") for n in range(3))
        assert [h.path for h in best_hits(hits, 2)] == ["2.md", "1.md"]

    def test_empty(self) -> None:
        assert best_hits([], 5) == []
