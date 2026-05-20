"""Report entity.

A ``Report`` aggregates one or more analyzer results for a particular
``Book``. It demonstrates *Association*: a Report references a Book.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from core.book import Book


class Report:
    """Holds analysis results for a single book.

    Args:
        book: The :class:`Book` this report is about.
    """

    def __init__(self, book: Book) -> None:
        self._book: Book = book
        self._results: Dict[str, Any] = {}
        self._created_at: str = (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def book(self) -> Book:
        """The book this report is about."""
        return self._book

    @property
    def results(self) -> Dict[str, Any]:
        """A copy of all analyzer results indexed by analyzer name."""
        return dict(self._results)

    @property
    def created_at(self) -> str:
        """ISO-8601 timestamp marking when the report was created."""
        return self._created_at

    # ------------------------------------------------------------------ #
    # Mutators
    # ------------------------------------------------------------------ #
    def add_result(self, analyzer_name: str, result: Dict[str, Any]) -> None:
        """Attach a single analyzer's output to the report."""
        self._results[analyzer_name] = result

    # ------------------------------------------------------------------ #
    # Serialization
    # ------------------------------------------------------------------ #
    def to_dict(self) -> Dict[str, Any]:
        """Return a fully-serialisable dictionary representation."""
        return {
            "book": {
                "title": self._book.title,
                "author": self._book.author,
                "filepath": self._book.filepath,
            },
            "created_at": self._created_at,
            "results": self._results,
        }

    def summary(self) -> str:
        """Return a human-readable multi-line summary of the report."""
        lines = [
            f"Report for {self._book}",
            f"Created: {self._created_at}",
            "-" * 48,
        ]
        if not self._results:
            lines.append("(no analyzers have run yet)")
        else:
            for name, result in self._results.items():
                lines.append(f"[{name}]")
                if isinstance(result, dict):
                    for key, value in result.items():
                        lines.append(f"  {key}: {value}")
                else:
                    lines.append(f"  {result}")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Dunder methods
    # ------------------------------------------------------------------ #
    def __repr__(self) -> str:
        return (
            f"Report(book={self._book.title!r}, "
            f"analyzers={list(self._results.keys())!r})"
        )
