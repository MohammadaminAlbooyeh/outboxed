"""The read side: polls the outbox table, dispatches to a backend, marks sent."""

from __future__ import annotations

import time

from sqlalchemy import func
from sqlalchemy.engine import Engine

from outboxed.backends.base import Backend
from outboxed.dedup import DeliveryTracker
from outboxed.models import outbox_table


class Relay:
    """Polls the outbox table and delivers undelivered events to a backend.

    At-least-once delivery: a crash between dispatch and marking an entry
    delivered means it is redelivered on restart. The ``DeliveryTracker``
    filters duplicates before they reach the backend's handler.
    """

    def __init__(
        self,
        engine: Engine,
        backend: Backend,
        *,
        batch_size: int = 100,
        poll_interval: float = 1.0,
        tracker: DeliveryTracker | None = None,
    ) -> None:
        self._engine = engine
        self._backend = backend
        self._batch_size = batch_size
        self._poll_interval = poll_interval
        self._tracker = tracker or DeliveryTracker()
        self._running = False

    def run_forever(self) -> None:
        self._running = True
        while self._running:
            delivered = self.poll_once()
            if delivered == 0:
                time.sleep(self._poll_interval)

    def stop(self) -> None:
        self._running = False

    def poll_once(self) -> int:
        delivered = 0
        with self._engine.begin() as conn:
            rows = conn.execute(
                outbox_table.select()
                .where(outbox_table.c.delivered_at.is_(None))
                .order_by(outbox_table.c.created_at)
                .limit(self._batch_size)
            ).fetchall()

            for row in rows:
                if not self._tracker.is_duplicate(row.id):
                    self._backend.publish(topic=row.topic, key=row.key, payload=row.payload)
                    self._tracker.mark_delivered(row.id)

                conn.execute(
                    outbox_table.update()
                    .where(outbox_table.c.id == row.id)
                    .values(delivered_at=func.now())
                )
                delivered += 1

        return delivered
