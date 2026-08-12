from collections import Counter, defaultdict
from collections.abc import Sequence

TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789'"
SENTENCE_ENDINGS = ".!?"


def tokenize(text: str) -> list[str]:
    cleaned = "".join(ch if ch in TOKEN_CHARS else " " for ch in text.lower())
    return [token for raw in cleaned.split() if (token := raw.strip("'"))]


def word_frequencies(text: str) -> dict[str, int]:
    return dict(Counter(tokenize(text)))


def top_words(text: str, n: int) -> list[tuple[str, int]]:
    counts = Counter(tokenize(text))
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def longest_words(text: str, n: int) -> list[str]:
    return sorted(set(tokenize(text)), key=lambda w: (-len(w), w))[:n]


def unique_word_ratio(text: str) -> float:
    tokens = tokenize(text)
    return len(set(tokens)) / len(tokens) if tokens else 0.0


def average_word_length(text: str) -> float:
    tokens = tokenize(text)
    return sum(len(t) for t in tokens) / len(tokens) if tokens else 0.0


def sentence_lengths(text: str) -> list[int]:
    table = str.maketrans(dict.fromkeys(SENTENCE_ENDINGS, "\n"))
    parts = text.translate(table).split("\n")
    return [len(tokens) for part in parts if (tokens := tokenize(part))]


def is_palindrome(text: str) -> bool:
    cleaned = "".join(ch for ch in text.lower() if ch.isalnum())
    return cleaned == cleaned[::-1]


def word_positions(text: str) -> dict[str, list[int]]:
    out: defaultdict[str, list[int]] = defaultdict(list)
    for index, token in enumerate(tokenize(text)):
        out[token].append(index)
    return dict(out)


def common_words(texts: Sequence[str]) -> set[str]:
    if not texts:
        return set()
    return set.intersection(*(set(tokenize(text)) for text in texts))
