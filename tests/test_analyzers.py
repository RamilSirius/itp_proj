"""Unit tests for analyzers, core entities and validators."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

# Make sure the project root is on sys.path even when this file is run by
# itself (e.g. ``python tests/test_analyzers.py``). When invoked through
# ``python -m unittest discover tests`` from the project root the cwd is
# already on the path, so this is a belt-and-braces measure.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from analyzers.phrases import PhraseAnalyzer  # noqa: E402
from analyzers.readability import ReadabilityAnalyzer  # noqa: E402
from analyzers.sentiment import SentimentAnalyzer  # noqa: E402
from core.book import Book  # noqa: E402
from core.library import Library  # noqa: E402
from core.report import Report  # noqa: E402
from utils.validators import is_valid_filename, split_sentences, tokenize_words  # noqa: E402


def _make_book(text: str, title: str = "tmp") -> Book:
    """Write *text* to a temp file and return a loaded :class:`Book`."""
    fd, path = tempfile.mkstemp(suffix=".txt", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    book = Book(title=title, filepath=path, author="tester")
    book.load()
    return book


class ReadabilityTests(unittest.TestCase):
    """Flesch Reading Ease behaviour."""

    def test_flesch_known_text(self) -> None:
        """A short, simple sentence should land in the 'easy' Flesch range."""
        text = "The cat sat on the mat. The dog ran fast."
        book = _make_book(text)
        try:
            result = ReadabilityAnalyzer().analyze(book)
        finally:
            os.remove(book.filepath)

        self.assertEqual(result["sentences"], 2)
        self.assertEqual(result["words"], 10)
        # Easy children's-book prose lands well above the 'easy' threshold.
        self.assertGreater(result["score"], 80)
        self.assertIn(result["interpretation"], {"very easy", "easy", "fairly easy"})


class SentimentTests(unittest.TestCase):
    """Lexicon-based sentiment classification."""

    def test_sentiment_positive(self) -> None:
        book = _make_book("I love this wonderful happy day.")
        try:
            result = SentimentAnalyzer().analyze(book)
        finally:
            os.remove(book.filepath)
        self.assertEqual(result["label"], "positive")
        self.assertGreater(result["polarity"], 0)
        self.assertGreaterEqual(result["positive_count"], 3)
        self.assertEqual(result["negative_count"], 0)

    def test_sentiment_negative(self) -> None:
        book = _make_book("Terrible awful horrible bad.")
        try:
            result = SentimentAnalyzer().analyze(book)
        finally:
            os.remove(book.filepath)
        self.assertEqual(result["label"], "negative")
        self.assertLess(result["polarity"], 0)
        self.assertGreaterEqual(result["negative_count"], 3)
        self.assertEqual(result["positive_count"], 0)


class PhraseTests(unittest.TestCase):
    """Top-phrase frequency analysis."""

    def test_phrase_counter(self) -> None:
        """'cat' should beat every other content word in this stop-word soup."""
        book = _make_book("the cat sat the cat ran")
        try:
            result = PhraseAnalyzer(top_n=5).analyze(book)
        finally:
            os.remove(book.filepath)
        top_words = result["top_words"]
        self.assertTrue(top_words, "expected at least one top word")
        self.assertEqual(top_words[0][0], "cat")
        self.assertEqual(top_words[0][1], 2)


class BookTests(unittest.TestCase):
    """Book loading and streaming behaviour."""

    def test_book_loads_file(self) -> None:
        book = _make_book("Hello world.\nSecond line here.\n", title="bk")
        try:
            self.assertTrue(book.metadata["loaded"])
            self.assertIn("Hello world", book.get_text())
            self.assertGreater(book.word_count(), 0)
            # Generator yields each non-empty line (newline stripped).
            lines = list(book.iter_lines())
            self.assertEqual(lines[0], "Hello world.")
            self.assertEqual(lines[1], "Second line here.")
        finally:
            os.remove(book.filepath)


class ValidatorTests(unittest.TestCase):
    """Regex-based filename validation."""

    def test_filename_regex_rejects_bad_input(self) -> None:
        self.assertFalse(is_valid_filename("../etc/passwd"))
        self.assertFalse(is_valid_filename("../sample.txt"))
        self.assertFalse(is_valid_filename("data/sample.txt"))
        self.assertFalse(is_valid_filename("sample.exe"))
        self.assertFalse(is_valid_filename(""))
        # Sanity: legitimate names still pass.
        self.assertTrue(is_valid_filename("alice.txt"))
        self.assertTrue(is_valid_filename("alice_in_wonderland.txt"))

    def test_tokenizer_and_sentence_splitter(self) -> None:
        words = tokenize_words("Hello, World! It's nice.")
        self.assertEqual(words, ["hello", "world", "it's", "nice"])
        sentences = split_sentences("One. Two? Three!")
        self.assertEqual(sentences, ["One.", "Two?", "Three!"])


class ReportTests(unittest.TestCase):
    """Report aggregation and serialisation."""

    def test_report_records_results(self) -> None:
        book = _make_book("Just some text.")
        try:
            library = Library()
            library.add_book(book)
            report = Report(book)
            report.add_result("DemoAnalyzer", {"score": 42})
            payload = report.to_dict()
            self.assertEqual(payload["book"]["title"], book.title)
            self.assertEqual(payload["results"]["DemoAnalyzer"]["score"], 42)
            self.assertIn("DemoAnalyzer", report.summary())
        finally:
            os.remove(book.filepath)


if __name__ == "__main__":
    unittest.main()
