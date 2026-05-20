"""Book entity.

A ``Book`` wraps a single ``.txt`` file on disk and exposes its content
through both an in-memory accessor (``get_text``) and a streaming generator
(``iter_lines``) that does not require loading the whole file at once.
"""

from __future__ import annotations

import os
import re
from typing import Iterator, Optional


class Book:
    """A single book loaded from a plain-text file.

    Attributes are encapsulated with a leading underscore. Read access is
    provided through ``@property`` accessors so external callers cannot
    mutate them directly.

    Args:
        title: Human-readable title.
        filepath: Absolute or relative path to the source ``.txt`` file.
        author: Optional author name (defaults to ``"Unknown"``).
    """

    _WORD_RE = re.compile(r"[A-Za-z']+")

    def __init__(self, title: str, filepath: str, author: str = "Unknown") -> None:
        self._title: str = title
        self._author: str = author
        self._filepath: str = filepath
        self._text: str = ""
        self._metadata: dict = {
            "loaded": False,
            "size_bytes": 0,
        }

    # ------------------------------------------------------------------ #
    # Properties (encapsulation)
    # ------------------------------------------------------------------ #
    @property
    def title(self) -> str:
        """Title of the book."""
        return self._title

    @property
    def author(self) -> str:
        """Author of the book."""
        return self._author

    @property
    def filepath(self) -> str:
        """Path to the source text file."""
        return self._filepath

    @property
    def metadata(self) -> dict:
        """Read-only copy of book metadata."""
        return dict(self._metadata)

    # ------------------------------------------------------------------ #
    # I/O
    # ------------------------------------------------------------------ #
    def load(self) -> str:
        """Read the file from disk into memory.

        Returns:
            The full text of the book.

        Raises:
            FileNotFoundError: If ``filepath`` does not exist.
            OSError: If the file cannot be read.
        """
        if not os.path.isfile(self._filepath):
            raise FileNotFoundError(f"Book file not found: {self._filepath}")
        try:
            with open(self._filepath, "r", encoding="utf-8", errors="replace") as fh:
                self._text = fh.read()
        except OSError as exc:
            raise OSError(f"Failed to read {self._filepath}: {exc}") from exc

        self._metadata["loaded"] = True
        self._metadata["size_bytes"] = os.path.getsize(self._filepath)
        return self._text

    def iter_lines(self) -> Iterator[str]:
        """Yield lines from the source file one at a time.

        This is a real generator: the file is opened lazily and each line is
        yielded as ``str`` (newline stripped). Suitable for very large books
        because it never materialises the full content.

        Yields:
            Each line of the file, with trailing newline removed.

        Raises:
            FileNotFoundError: If the source file is missing.
        """
        if not os.path.isfile(self._filepath):
            raise FileNotFoundError(f"Book file not found: {self._filepath}")
        with open(self._filepath, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                yield line.rstrip("\n")

    # ------------------------------------------------------------------ #
    # Accessors
    # ------------------------------------------------------------------ #
    def get_text(self) -> str:
        """Return the loaded text. Calls :meth:`load` lazily if needed."""
        if not self._metadata["loaded"]:
            self.load()
        return self._text

    def word_count(self) -> int:
        """Count the words in the book using a simple regex tokenizer."""
        text = self.get_text()
        return len(self._WORD_RE.findall(text))

    # ------------------------------------------------------------------ #
    # Dunder methods
    # ------------------------------------------------------------------ #
    def __str__(self) -> str:
        return f"{self._title} by {self._author}"

    def __repr__(self) -> str:
        return f"Book(title={self._title!r}, author={self._author!r}, path={self._filepath!r})"
