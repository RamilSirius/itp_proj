"""Abstract base class for all analyzers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from core.book import Book


class BaseAnalyzer(ABC):
    """Common interface every analyzer must implement.

    Subclasses must override :meth:`analyze`. The :attr:`name` property is
    used by ``main.py`` and :class:`core.report.Report` to label results.
    """

    #: Human-readable name shown in reports. Subclasses override this.
    NAME: str = "BaseAnalyzer"

    @property
    def name(self) -> str:
        """Return the analyzer's human-readable name."""
        return self.NAME

    @abstractmethod
    def analyze(self, book: Book) -> Dict[str, Any]:
        """Analyze *book* and return a dict of results.

        Args:
            book: The :class:`Book` to analyze.

        Returns:
            A dictionary of result keys to values. The exact contents depend
            on the concrete analyzer.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r})"
