"""Regex-based validators and tokenizers.

Centralised so the analyzers and the CLI share a single source of truth
for what a "word", a "sentence" and a "valid filename" look like.
"""

from __future__ import annotations

import os
import re
from typing import List

# A safe ``data/`` filename: letters, digits, dot, dash, underscore, must end
# in ``.txt``. Path separators are explicitly disallowed to block traversal.
_FILENAME_RE = re.compile(r"^[A-Za-z0-9_\-]+(?:\.[A-Za-z0-9_\-]+)*\.txt$")

# Word tokenizer: contiguous letters with optional inner apostrophe.
_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

# Sentence splitter: split on . ! ? followed by whitespace or EOS.
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def is_valid_filename(name: str) -> bool:
    """Return ``True`` if *name* is a safe ``.txt`` filename.

    The check rejects anything containing path separators, parent-directory
    traversal (``..``), or characters outside ``[A-Za-z0-9_.\\-]``. Only files
    that end in ``.txt`` are accepted.

    Examples:
        >>> is_valid_filename("alice.txt")
        True
        >>> is_valid_filename("../etc/passwd")
        False
    """
    if not isinstance(name, str) or not name:
        return False
    if os.sep in name or "/" in name or "\\" in name:
        return False
    if ".." in name:
        return False
    return bool(_FILENAME_RE.match(name))


def tokenize_words(text: str) -> List[str]:
    """Split *text* into lowercase word tokens using regex."""
    return [m.group(0).lower() for m in _WORD_RE.finditer(text)]


def split_sentences(text: str) -> List[str]:
    """Split *text* into a list of non-empty sentences using regex."""
    if not text:
        return []
    parts = _SENTENCE_RE.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def parse_menu_choice(raw: str, valid: List[str]) -> str:
    """Validate raw CLI input against a list of allowed choices.

    Returns:
        The trimmed input if it matches one of *valid*.

    Raises:
        ValueError: If the input is empty or not in *valid*.
    """
    if raw is None:
        raise ValueError("No input provided.")
    cleaned = raw.strip()
    if not cleaned:
        raise ValueError("Input is empty.")
    if cleaned not in valid:
        raise ValueError(f"{cleaned!r} is not one of {valid}.")
    return cleaned
