"""Grader for ex02_text_stats."""

import pytest

from modules.m01_language_core.exercises.ex02_text_stats import (
    average_word_length,
    common_words,
    is_palindrome,
    longest_words,
    sentence_lengths,
    tokenize,
    top_words,
    unique_word_ratio,
    word_frequencies,
    word_positions,
)


class TestTokenize:
    def test_lowercases_and_strips_punctuation(self) -> None:
        assert tokenize("Hello, World! It's 2026 -- ready?") == [
            "hello",
            "world",
            "it's",
            "2026",
            "ready",
        ]

    def test_strips_surrounding_apostrophes_only(self) -> None:
        assert tokenize("''quoted'' don't") == ["quoted", "don't"]

    @pytest.mark.parametrize("text", ["", "   ", "...", "!!! ??? ---"])
    def test_no_tokens(self, text: str) -> None:
        assert tokenize(text) == []

    def test_keeps_digits_and_alphanumerics(self) -> None:
        assert tokenize("v2 gpt-4o 3.14") == ["v2", "gpt", "4o", "3", "14"]

    def test_collapses_all_whitespace(self) -> None:
        assert tokenize("a\tb\nc  d") == ["a", "b", "c", "d"]


class TestWordFrequencies:
    def test_counts(self) -> None:
        assert word_frequencies("the cat the hat") == {"the": 2, "cat": 1, "hat": 1}

    def test_case_insensitive_via_tokenize(self) -> None:
        assert word_frequencies("The THE the") == {"the": 3}

    def test_empty(self) -> None:
        assert word_frequencies("") == {}


class TestTopWords:
    def test_ties_are_alphabetical(self) -> None:
        assert top_words("b a b c a", 2) == [("a", 2), ("b", 2)]

    def test_count_desc(self) -> None:
        assert top_words("x x x y y z", 3) == [("x", 3), ("y", 2), ("z", 1)]

    def test_n_larger_than_vocabulary(self) -> None:
        assert top_words("solo", 5) == [("solo", 1)]

    def test_empty(self) -> None:
        assert top_words("", 3) == []


class TestLongestWords:
    def test_distinct_and_length_desc(self) -> None:
        assert longest_words("epsilon alpha beta gamma alpha", 2) == ["epsilon", "alpha"]

    def test_equal_length_ties_alphabetical(self) -> None:
        assert longest_words("beta alpha gamma", 3) == ["alpha", "gamma", "beta"]

    def test_empty(self) -> None:
        assert longest_words("", 2) == []


class TestUniqueWordRatio:
    def test_half(self) -> None:
        assert unique_word_ratio("a b a b") == pytest.approx(0.5)

    def test_all_unique(self) -> None:
        assert unique_word_ratio("a b c") == pytest.approx(1.0)

    def test_no_words_is_zero_not_an_error(self) -> None:
        assert unique_word_ratio("!!!") == 0.0


class TestAverageWordLength:
    def test_mean(self) -> None:
        assert average_word_length("ab cde") == pytest.approx(2.5)

    def test_no_words_is_zero(self) -> None:
        assert average_word_length("") == 0.0


class TestSentenceLengths:
    def test_three_sentences(self) -> None:
        assert sentence_lengths("Hi there. How are you? Fine!") == [2, 3, 1]

    def test_missing_terminator_still_counts(self) -> None:
        assert sentence_lengths("no terminator here") == [3]

    def test_skips_empty_sentences(self) -> None:
        assert sentence_lengths("One... Two!!  ") == [1, 1]

    def test_empty(self) -> None:
        assert sentence_lengths("") == []


class TestIsPalindrome:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("A man, a plan, a canal: Panama", True),
            ("No 'x' in Nixon", True),
            ("racecar", True),
            ("hello", False),
            ("ab", False),
            ("", True),
            ("!!!", True),
            ("12321", True),
        ],
    )
    def test_cases(self, text: str, expected: bool) -> None:
        assert is_palindrome(text) is expected


class TestWordPositions:
    def test_inverted_index(self) -> None:
        assert word_positions("the cat the hat") == {"the": [0, 2], "cat": [1], "hat": [3]}

    def test_positions_are_token_indexes_not_character_offsets(self) -> None:
        assert word_positions("aaa b") == {"aaa": [0], "b": [1]}

    def test_empty(self) -> None:
        assert word_positions("") == {}


class TestCommonWords:
    def test_intersection(self) -> None:
        assert common_words(["a b c", "b c d", "c b e"]) == {"b", "c"}

    def test_no_overlap(self) -> None:
        assert common_words(["a", "b"]) == set()

    def test_single_text_returns_its_own_vocabulary(self) -> None:
        assert common_words(["a b a"]) == {"a", "b"}

    def test_empty_sequence(self) -> None:
        assert common_words([]) == set()
