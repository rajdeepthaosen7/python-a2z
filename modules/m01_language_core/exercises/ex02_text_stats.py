"""Exercise 02 — strings, Counter, normalization.

This is the tokenizer you will reuse in Athena Stage 1, and conceptually the
same preprocessing step that sits in front of every retrieval system you'll
build in Phase 4.

Run:  uv run pytest modules/m01_language_core/tests/test_ex02_text_stats.py -x -q

Constraints:
  * Use `collections.Counter` where it fits.
  * `word_frequencies`, `top_words`, `longest_words`, `average_word_length`
    must all call `tokenize` — do not re-implement splitting.
  * No regex required, but `re` is allowed if you prefer it.
"""

from collections.abc import Sequence

# A token character is a letter, a digit, or an apostrophe.
TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789'"
SENTENCE_ENDINGS = ".!?"


def tokenize(text: str) -> list[str]:
    """Split text into normalized word tokens.

    Rules, in order:
      1. Lowercase the whole text.
      2. A raw token is a maximal run of characters from TOKEN_CHARS.
      3. Strip leading and trailing apostrophes from each raw token.
      4. Discard anything that is now empty.

    >>> tokenize("Hello, World! It's 2026 -- ready?")
    ["hello", "world", "it's", "2026", "ready"]
    >>> tokenize("''quoted''")
    ['quoted']
    >>> tokenize("   ")
    []
    """
    raise NotImplementedError


def word_frequencies(text: str) -> dict[str, int]:
    """Count how often each token appears.

    >>> word_frequencies("the cat the hat")
    {'the': 2, 'cat': 1, 'hat': 1}

    Return a plain dict (a Counter is a dict, so returning one is fine).
    """
    raise NotImplementedError


def top_words(text: str, n: int) -> list[tuple[str, int]]:
    """Return the n most frequent (word, count) pairs.

    Sort by count descending, then by word ascending. Deterministic output is
    a hard requirement — `Counter.most_common` alone does NOT give you that,
    because it leaves ties in insertion order. Think about how to fix it.

    >>> top_words("b a b c a", 2)
    [('a', 2), ('b', 2)]
    """
    raise NotImplementedError


def longest_words(text: str, n: int) -> list[str]:
    """Return the n longest DISTINCT words.

    Sort by length descending, then alphabetically ascending.

    >>> longest_words("epsilon alpha beta gamma alpha", 2)
    ['epsilon', 'alpha']
    """
    raise NotImplementedError


def unique_word_ratio(text: str) -> float:
    """Return distinct-token count / total-token count.

    Returns 0.0 when there are no tokens (do not raise ZeroDivisionError).
    This metric is called lexical diversity, and you'll use it again in
    Module 18 to detect degenerate LLM output.

    >>> unique_word_ratio("a b a b")
    0.5
    """
    raise NotImplementedError


def average_word_length(text: str) -> float:
    """Return the mean token length, or 0.0 when there are no tokens.

    >>> average_word_length("ab cde")
    2.5
    """
    raise NotImplementedError


def sentence_lengths(text: str) -> list[int]:
    """Return the token count of each non-empty sentence.

    Sentences are separated by any character in SENTENCE_ENDINGS. Sentences
    that contain no tokens are omitted entirely.

    >>> sentence_lengths("Hi there. How are you? Fine!")
    [2, 3, 1]
    >>> sentence_lengths("no terminator here")
    [3]
    """
    raise NotImplementedError


def is_palindrome(text: str) -> bool:
    """True if text reads the same backwards, ignoring case and non-alphanumerics.

    Empty (or punctuation-only) input is a palindrome.

    >>> is_palindrome("A man, a plan, a canal: Panama")
    True
    >>> is_palindrome("hello")
    False

    Hint: build the cleaned string, then compare it to its own [::-1] slice.
    """
    raise NotImplementedError


def word_positions(text: str) -> dict[str, list[int]]:
    """Map each token to the sorted list of token-indexes where it appears.

    This is an inverted index for one document — the core data structure of
    Athena Stage 1 and of every keyword search engine ever built.

    >>> word_positions("the cat the hat")
    {'the': [0, 2], 'cat': [1], 'hat': [3]}
    """
    raise NotImplementedError


def common_words(texts: Sequence[str]) -> set[str]:
    """Return the set of tokens present in EVERY text.

    An empty `texts` sequence gives an empty set.

    >>> sorted(common_words(["a b c", "b c d", "c b e"]))
    ['b', 'c']

    Hint: set.intersection accepts multiple iterables, and functools.reduce
    exists. Both are fine — pick the one a reviewer would thank you for.
    """
    raise NotImplementedError
