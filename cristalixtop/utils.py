from __future__ import annotations

from typing import Iterable, Sequence, TypeVar

from .errors import CristalixValidationError

T = TypeVar("T")


def ensure_non_empty(value: str, name: str) -> None:
    if not value:
        raise CristalixValidationError(f"{name} is required")


def ensure_max_items(items: Sequence[T], limit: int, name: str) -> None:
    if len(items) > limit:
        raise CristalixValidationError(f"{name} must contain at most {limit} items")


def ensure_not_empty(items: Sequence[T], name: str) -> None:
    if len(items) == 0:
        raise CristalixValidationError(f"{name} must not be empty")


def ensure_limit(limit: int, *, max_limit: int = 100) -> None:
    if limit <= 0:
        raise CristalixValidationError("limit must be positive")
    if limit > max_limit:
        raise CristalixValidationError(f"limit must be <= {max_limit}")


def ensure_skip(skip: int) -> None:
    if skip < 0:
        raise CristalixValidationError("skip must be >= 0")


def to_list(values: Iterable[T]) -> list[T]:
    return list(values)
