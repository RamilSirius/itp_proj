"""Lexicon-based sentiment analyzer."""

from __future__ import annotations

from typing import Any, Dict

from analyzers.base import BaseAnalyzer
from core.book import Book
from utils.decorators import log_action
from utils.stopwords import NEGATIVE_WORDS, POSITIVE_WORDS
from utils.validators import tokenize_words


def _label(ratio: float) -> str:
    """Translate a polarity ratio in ``[-1, 1]`` into a coarse label."""
    if ratio > 0.05:
        return "positive"
    if ratio < -0.05:
        return "negative"
    return "neutral"


class SentimentAnalyzer(BaseAnalyzer):
    """Count positive vs. negative words using a built-in lexicon."""

    NAME = "Sentiment"

    @log_action
    def analyze(self, book: Book) -> Dict[str, Any]:
        words = tokenize_words(book.get_text())

        # `filter` is used for *both* polarity buckets to keep the
        # functional-programming requirement explicit and visible.
        positive_hits = list(filter(lambda w: w in POSITIVE_WORDS, words))
        negative_hits = list(filter(lambda w: w in NEGATIVE_WORDS, words))

        positive = len(positive_hits)
        negative = len(negative_hits)
        total = positive + negative
        ratio = (positive - negative) / total if total else 0.0

        return {
            "positive_count": positive,
            "negative_count": negative,
            "polarity": round(ratio, 3),
            "label": _label(ratio),
            "total_emotional_words": total,
        }
