"""Library entity.

A ``Library`` is an in-memory collection of ``Book`` objects keyed by title.
It demonstrates *Association*: a Library has-many Books.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from core.book import Book


class Library:
    """Manages a collection of :class:`Book` objects.

    The Library owns its book dictionary and provides simple add/remove/list
    operations plus persistence to a JSON state file.
    """

    def __init__(self) -> None:
        self._books: Dict[str, Book] = {}

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def size(self) -> int:
        """Number of books currently held."""
        return len(self._books)

    # ------------------------------------------------------------------ #
    # Mutators
    # ------------------------------------------------------------------ #
    def add_book(self, book: Book) -> None:
        """Add a book to the library, keyed by its title.

        Raises:
            ValueError: If a book with the same title already exists.
        """
        if book.title in self._books:
            raise ValueError(f"A book titled {book.title!r} already exists.")
        self._books[book.title] = book

    def remove_book(self, title: str) -> Book:
        """Remove and return the book with the given title.

        Raises:
            KeyError: If no such book is registered.
        """
        if title not in self._books:
            raise KeyError(f"No book titled {title!r} in library.")
        return self._books.pop(title)

    # ------------------------------------------------------------------ #
    # Accessors
    # ------------------------------------------------------------------ #
    def get_book(self, title: str) -> Optional[Book]:
        """Return the book with the given title or ``None`` if absent."""
        return self._books.get(title)

    def list_books(self) -> List[Book]:
        """Return a list of all books in stable insertion order."""
        return list(self._books.values())

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def save_state(self, path: str) -> None:
        """Persist the library's metadata (titles, authors, paths) to JSON.

        Only the metadata is saved — the text contents stay on disk in the
        original ``.txt`` files.
        """
        payload = [
            {"title": b.title, "author": b.author, "filepath": b.filepath}
            for b in self._books.values()
        ]
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            raise OSError(f"Failed to write library state to {path}: {exc}") from exc

    def load_state(self, path: str) -> None:
        """Restore a library from a JSON state file produced by :meth:`save_state`.

        Existing books are replaced.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Library state file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            raise OSError(f"Failed to read library state {path}: {exc}") from exc

        self._books.clear()
        for entry in payload:
            book = Book(
                title=entry["title"],
                filepath=entry["filepath"],
                author=entry.get("author", "Unknown"),
            )
            self._books[book.title] = book

    # ------------------------------------------------------------------ #
    # Dunder methods
    # ------------------------------------------------------------------ #
    def __contains__(self, title: str) -> bool:
        return title in self._books

    def __iter__(self):
        return iter(self._books.values())

    def __len__(self) -> int:
        return len(self._books)

    def __repr__(self) -> str:
        return f"Library(size={self.size})"
