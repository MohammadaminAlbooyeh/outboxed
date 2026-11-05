"""A redelivered event id must never reach the backend's handler twice."""

from outboxed.dedup import DeliveryTracker


def test_mark_delivered_then_is_duplicate():
    tracker = DeliveryTracker()
    assert not tracker.is_duplicate("evt-1")

    tracker.mark_delivered("evt-1")

    assert tracker.is_duplicate("evt-1")
    assert not tracker.is_duplicate("evt-2")
