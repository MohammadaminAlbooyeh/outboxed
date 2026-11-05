# Delivery guarantees

outboxed is built around one explicit claim:

> Once a transaction commits, its event is delivered at least once, and
> never silently dropped.

## What this means precisely

- **Write side**: `Outbox.enqueue()` only has an effect if the surrounding
  transaction commits. A rollback removes the row along with everything
  else in that transaction. There is no window where the write succeeds but
  the event is lost, because they're the same atomic operation.
- **Relay side**: the relay polls for undelivered rows, dispatches them to
  the backend, and only then marks them delivered. If the relay process
  dies after dispatch but before marking the row delivered, the row is
  redelivered on the next poll.
- **At-least-once, not exactly-once, at the transport layer**: a crash in
  that window means the backend may see the same event twice. outboxed's
  `DeliveryTracker` filters those duplicates by event id before they reach
  your handler, so the event is *observed* exactly once downstream even
  though the broker may have transported it more than once.

## How this is tested

`tests/test_chaos_crash_recovery.py` starts a relay, kills the process
(simulated) mid-batch at a randomized point, restarts it, and asserts that
every committed event eventually reaches the backend, and that none of them
are observed twice. That test runs in CI on every commit — it is not a
README promise.

## What outboxed does not guarantee

- **Ordering across topics**: ordering is only guaranteed within a single
  topic/key, and only as strongly as the underlying broker preserves it.
- **Delivery latency**: this is a polling relay, not a push system. Latency
  is bounded by the poll interval, not by the broker's own latency.
