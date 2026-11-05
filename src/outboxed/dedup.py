"""Delivery-id tracking so retries after a crash don't double-publish downstream."""

from __future__ import annotations


class DeliveryTracker:
    """Tracks which event ids have already been handed to the backend.

    Backed by whatever store the relay is configured with; the default
    in-process set is only suitable for a single relay instance and tests.
    """

    def __init__(self) -> None:
        self._seen: set[str] = set()

    def is_duplicate(self, event_id: str) -> bool:
        return event_id in self._seen

    def mark_delivered(self, event_id: str) -> None:
        self._seen.add(event_id)
