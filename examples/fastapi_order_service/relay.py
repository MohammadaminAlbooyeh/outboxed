"""Standalone relay process for the order service example.

Run alongside main.py:

    python relay.py
"""

from sqlalchemy import create_engine

from outboxed import Relay
from outboxed.backends.in_memory import InMemoryBackend

DATABASE_URL = "postgresql://outboxed:outboxed@localhost:5432/outboxed"


def main() -> None:
    engine = create_engine(DATABASE_URL)
    backend = InMemoryBackend()  # swap for KafkaBackend/RedisStreamsBackend/SQSBackend
    relay = Relay(engine, backend)

    print("relay running, polling for outbox entries...")
    relay.run_forever()


if __name__ == "__main__":
    main()
