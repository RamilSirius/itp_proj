"""Core domain entities for Book Analyzer.

Exposes the three domain classes used across the project:
``Book``, ``Library`` and ``Report``.
"""

from core.book import Book
from core.library import Library
from core.report import Report

__all__ = ["Book", "Library", "Report"]
