"""Top-phrase analyzer (unigrams + bigrams)."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Tuple

from analyzers.base import BaseAnalyzer
from core.book import Book
from utils.decorators import log_action
from utils.stopwords import STOPWORDS
from utils.validators import tokenize_words


class PhraseAnalyzer(BaseAnalyzer):
    """Find the most frequent words and bigrams in a book.

    Args:
        top_n: How many top entries to return for each list. Defaults to 10.
    """

    NAME = "TopPhrases"

    def __init__(self, top_n: int = 10) -> None:
        self._top_n = top_n

    @property
    def top_n(self) -> int:
        """Number of top entries returned per list."""
        return self._top_n

    @log_action
    def analyze(self, book: Book) -> Dict[str, Any]:
        all_words = tokenize_words(book.get_text())

        # Stop-word removal via `filter` -- functional style, single pass.
        content_words: List[str] = list(filter(lambda w: w not in STOPWORDS, all_words))

        unigram_counter: Counter[str] = Counter(content_words)

        # Build bigrams from the *original* token stream so adjacency is
        # preserved, but only keep bigrams whose words are both content words.
        bigrams: List[Tuple[str, str]] = [
            (a, b)
            for a, b in zip(all_words, all_words[1:])
            if a not in STOPWORDS and b not in STOPWORDS
        ]
        bigram_counter: Counter[Tuple[str, str]] = Counter(bigrams)

        # `lambda` for sort key on tuples (count desc, then alphabetical).
        top_words = sorted(
            unigram_counter.items(),
            key=lambda item: (-item[1], item[0]),
        )[: self._top_n]

        top_bigrams = sorted(
            bigram_counter.items(),
            key=lambda item: (-item[1], item[0]),
        )[: self._top_n]

        return {
            "top_words": [(word, count) for word, count in top_words],
            "top_bigrams": [(" ".join(pair), count) for pair, count in top_bigrams],
            "unique_content_words": len(unigram_counter),
            "total_content_words": len(content_words),
        }
