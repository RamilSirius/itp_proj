"""Flesch Reading Ease analyzer."""

from __future__ import annotations

import re
from typing import Any, Dict

from analyzers.base import BaseAnalyzer
from core.book import Book
from utils.decorators import log_action
from utils.validators import split_sentences, tokenize_words


_VOWEL_GROUPS_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)


def _count_syllables(word: str) -> int:
    """Estimate syllables in *word* using a vowel-group heuristic.

    The rule: count vowel groups, subtract 1 for a trailing silent "e",
    and never return less than 1 for a non-empty word. This is the same
    approximation used by most pedagogical Flesch implementations.
    """
    if not word:
        return 0
    word = word.lower()
    groups = _VOWEL_GROUPS_RE.findall(word)
    count = len(groups)
    if word.endswith("e") and count > 1 and not word.endswith("le"):
        count -= 1
    return max(1, count)


def _interpret(score: float) -> str:
    """Map a Flesch score to a textual label."""
    if score >= 90:
        return "very easy"
    if score >= 80:
        return "easy"
    if score >= 70:
        return "fairly easy"
    if score >= 60:
        return "standard"
    if score >= 50:
        return "fairly difficult"
    if score >= 30:
        return "difficult"
    return "very difficult"


class ReadabilityAnalyzer(BaseAnalyzer):
    """Compute the Flesch Reading Ease score.

    Formula: ``206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)``.
    """

    NAME = "Readability"

    @log_action
    def analyze(self, book: Book) -> Dict[str, Any]:
        text = book.get_text()
        words = tokenize_words(text)
        sentences = split_sentences(text)

        # `map` produces an iterator of per-word syllable counts -- consumed
        # via sum() so we never materialise the intermediate list.
        total_syllables = sum(map(_count_syllables, words))

        word_count = len(words)
        sentence_count = max(1, len(sentences))

        if word_count == 0:
            return {
                "score": 0.0,
                "interpretation": "empty",
                "words": 0,
                "sentences": 0,
                "syllables": 0,
            }

        score = (
            206.835
            - 1.015 * (word_count / sentence_count)
            - 84.6 * (total_syllables / word_count)
        )
        return {
            "score": round(score, 2),
            "interpretation": _interpret(score),
            "words": word_count,
            "sentences": sentence_count,
            "syllables": total_syllables,
        }
