"""Reusable decorators for the project."""

from __future__ import annotations

import functools
import sys
import time
from typing import Any, Callable


def log_action(func: Callable[..., Any]) -> Callable[..., Any]:
    """Log the start, finish and elapsed time of a method call.

    Designed to be applied to analyzer ``analyze()`` methods. The decorator
    prints to ``stderr`` so the surrounding CLI output stays clean. When
    applied to a bound method, the owning class name is included so
    polymorphic dispatch is easy to follow at runtime.

    Args:
        func: The function or method being wrapped.

    Returns:
        A wrapper that calls ``func`` and emits log lines around it.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        owner = ""
        if args:
            owner = type(args[0]).__name__ + "."
        label = f"{owner}{func.__name__}"
        start = time.perf_counter()
        print(f"[log_action] -> {label} starting", file=sys.stderr)
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            elapsed = time.perf_counter() - start
            print(
                f"[log_action] !! {label} raised {type(exc).__name__} after {elapsed:.4f}s",
                file=sys.stderr,
            )
            raise
        elapsed = time.perf_counter() - start
        print(f"[log_action] <- {label} done in {elapsed:.4f}s", file=sys.stderr)
        return result

    return wrapper
