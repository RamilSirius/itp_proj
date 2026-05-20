"""Pluggable text analyzers."""

from analyzers.base import BaseAnalyzer
from analyzers.readability import ReadabilityAnalyzer
from analyzers.sentiment import SentimentAnalyzer
from analyzers.phrases import PhraseAnalyzer

__all__ = [
    "BaseAnalyzer",
    "ReadabilityAnalyzer",
    "SentimentAnalyzer",
    "PhraseAnalyzer",
]
