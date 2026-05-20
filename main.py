"""Book Analyzer — interactive CLI entry point.

Run ``python main.py`` to launch the menu, or ``python main.py --demo`` to
execute the canonical "load sample, run all analyzers, save report" flow
non-interactively.
"""

from __future__ import annotations

import os
import sys
from typing import List, Optional

from analyzers import (
    BaseAnalyzer,
    PhraseAnalyzer,
    ReadabilityAnalyzer,
    SentimentAnalyzer,
)
from core.book import Book
from core.library import Library
from core.report import Report
from utils.storage import report_to_csv, report_to_json
from utils.validators import is_valid_filename, parse_menu_choice


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
STATE_FILE = os.path.join(REPORTS_DIR, "library_state.json")


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #
def _all_analyzers() -> List[BaseAnalyzer]:
    """Construct the canonical list of analyzers used for "run all"."""
    return [ReadabilityAnalyzer(), SentimentAnalyzer(), PhraseAnalyzer()]


def _print_menu() -> None:
    print()
    print("=== Book Analyzer ===")
    print("1. Load a book from data/")
    print("2. List books in library")
    print("3. Analyze a book")
    print("4. View last report")
    print("5. Save report (JSON / CSV)")
    print("6. Load saved library state")
    print("0. Exit")


def _print_analyze_menu() -> None:
    print()
    print("--- Analyze ---")
    print("1. Readability (Flesch)")
    print("2. Sentiment")
    print("3. Top phrases")
    print("4. Run ALL analyzers")
    print("0. Back")


def _select_book(library: Library) -> Optional[Book]:
    """Prompt the user to pick a book by index. Returns ``None`` on cancel."""
    books = library.list_books()
    if not books:
        print("Library is empty. Load a book first (option 1).")
        return None
    for idx, book in enumerate(books, start=1):
        print(f"  {idx}. {book}")
    raw = input("Pick a book number (or blank to cancel): ")
    raw = raw.strip()
    if not raw:
        return None
    try:
        position = int(raw)
    except ValueError:
        print(f"Not a number: {raw!r}")
        return None
    if position < 1 or position > len(books):
        print(f"Out of range: {position}")
        return None
    return books[position - 1]


def _run_analyzers(book: Book, analyzers: List[BaseAnalyzer]) -> Report:
    """Run each analyzer over *book* polymorphically and collect a Report."""
    report = Report(book)
    # Polymorphism: each `analyzer` is a subclass of BaseAnalyzer; we don't
    # care which one -- we just call .analyze(book) on each.
    for analyzer in analyzers:
        try:
            result = analyzer.analyze(book)
        except Exception as exc:  # noqa: BLE001 - want to keep CLI alive
            print(f"  ! {analyzer.name} failed: {exc}")
            continue
        report.add_result(analyzer.name, result)
    return report


# ---------------------------------------------------------------------- #
# Menu actions
# ---------------------------------------------------------------------- #
def action_load_book(library: Library) -> None:
    """Prompt the user for a filename inside ``data/`` and add it to the library."""
    available = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".txt")]
    if available:
        print("Available files in data/:")
        for f in available:
            print(f"  - {f}")
    else:
        print("No .txt files found in data/.")

    filename = input("Filename to load (e.g. sample.txt): ").strip()
    if not filename:
        print("Cancelled.")
        return
    if not is_valid_filename(filename):
        print(f"Refused: {filename!r} is not a valid plain .txt filename.")
        return

    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return

    title = input("Title (blank to use filename): ").strip() or filename
    author = input("Author (blank for Unknown): ").strip() or "Unknown"

    try:
        book = Book(title=title, filepath=filepath, author=author)
        book.load()
        library.add_book(book)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"Failed to load book: {exc}")
        return
    print(f"Loaded: {book} ({book.word_count()} words)")


def action_list_books(library: Library) -> None:
    """Print every book currently held by *library*."""
    books = library.list_books()
    if not books:
        print("Library is empty.")
        return
    print(f"{len(books)} book(s) in the library:")
    for book in books:
        print(f"  - {book}  [{book.filepath}]")


def action_analyze(library: Library, last_report: List[Optional[Report]]) -> None:
    """Run the analyze sub-menu, updating ``last_report[0]`` on success."""
    book = _select_book(library)
    if book is None:
        return

    _print_analyze_menu()
    raw = input("Choice: ")
    try:
        choice = parse_menu_choice(raw, ["0", "1", "2", "3", "4"])
    except ValueError as exc:
        print(f"Invalid: {exc}")
        return

    if choice == "0":
        return

    if choice == "1":
        analyzers = [ReadabilityAnalyzer()]
    elif choice == "2":
        analyzers = [SentimentAnalyzer()]
    elif choice == "3":
        analyzers = [PhraseAnalyzer()]
    else:
        analyzers = _all_analyzers()

    report = _run_analyzers(book, analyzers)
    last_report[0] = report
    print()
    print(report.summary())


def action_view_report(last_report: List[Optional[Report]]) -> None:
    """Print the most recently generated report, if any."""
    report = last_report[0]
    if report is None:
        print("No report yet. Run option 3 first.")
        return
    print(report.summary())


def action_save_report(last_report: List[Optional[Report]]) -> None:
    """Save the latest report in JSON, CSV, or both."""
    report = last_report[0]
    if report is None:
        print("No report to save. Run option 3 first.")
        return
    print("Save as: 1=JSON  2=CSV  3=BOTH  0=Cancel")
    raw = input("Choice: ")
    try:
        choice = parse_menu_choice(raw, ["0", "1", "2", "3"])
    except ValueError as exc:
        print(f"Invalid: {exc}")
        return
    if choice == "0":
        return
    try:
        if choice == "1" or choice == "3":
            path = report_to_json(report, REPORTS_DIR)
            print(f"  JSON -> {path}")
        if choice == "2" or choice == "3":
            path = report_to_csv(report, REPORTS_DIR)
            print(f"  CSV  -> {path}")
    except OSError as exc:
        print(f"Failed to save report: {exc}")


def action_load_state(library: Library) -> None:
    """Reload the library from the on-disk state file."""
    if not os.path.isfile(STATE_FILE):
        print(f"No saved state at {STATE_FILE}.")
        return
    try:
        library.load_state(STATE_FILE)
    except (FileNotFoundError, OSError) as exc:
        print(f"Failed to load state: {exc}")
        return
    print(f"Restored {len(library)} book(s).")


# ---------------------------------------------------------------------- #
# Demo and main loop
# ---------------------------------------------------------------------- #
def run_demo() -> int:
    """Non-interactive scripted run: load sample.txt, run all, save report."""
    library = Library()
    sample_path = os.path.join(DATA_DIR, "sample.txt")
    if not os.path.isfile(sample_path):
        print(f"Demo failed: missing {sample_path}", file=sys.stderr)
        return 1

    book = Book(title="sample.txt", filepath=sample_path, author="Lewis Carroll")
    book.load()
    library.add_book(book)
    print(f"Loaded: {book} ({book.word_count()} words)")

    report = _run_analyzers(book, _all_analyzers())
    print()
    print(report.summary())

    json_path = report_to_json(report, REPORTS_DIR)
    csv_path = report_to_csv(report, REPORTS_DIR)
    print()
    print(f"Saved JSON -> {json_path}")
    print(f"Saved CSV  -> {csv_path}")
    library.save_state(STATE_FILE)
    print(f"Saved library state -> {STATE_FILE}")
    return 0


def main() -> int:
    """Run the interactive CLI loop until the user picks 0 (Exit)."""
    if "--demo" in sys.argv[1:]:
        return run_demo()

    library = Library()
    last_report: List[Optional[Report]] = [None]

    while True:
        _print_menu()
        try:
            raw = input("Choice: ")
        except EOFError:
            print()
            return 0
        try:
            choice = parse_menu_choice(raw, ["0", "1", "2", "3", "4", "5", "6"])
        except ValueError as exc:
            print(f"Invalid: {exc}")
            continue

        if choice == "0":
            print("Bye.")
            return 0
        elif choice == "1":
            action_load_book(library)
        elif choice == "2":
            action_list_books(library)
        elif choice == "3":
            action_analyze(library, last_report)
        elif choice == "4":
            action_view_report(last_report)
        elif choice == "5":
            action_save_report(last_report)
        elif choice == "6":
            action_load_state(library)


if __name__ == "__main__":
    raise SystemExit(main())
