# The dual-write problem

A common backend shape is: write a row to the database, then publish an
event about it (an order placed, a payment captured, a user created). Doing
these as two separate operations is the dual-write problem.

```
   business write          publish event
  ┌───────────────┐      ┌─────────────────┐
  │  INSERT order  │ ---> │  producer.send   │
  └───────────────┘      └─────────────────┘
        commits                 ??? crash here means the
                                 event is lost forever
```

If the process crashes between the database commit and the publish call,
the event is lost forever, and nothing else in the system knows the write
ever happened. Retrying blindly trades that failure for the opposite one:
duplicate events on every retry that succeeds after a delayed
acknowledgment.

## The fix

Never make that second call directly. Instead, insert the event as a row in
an "outbox" table, in the *same database transaction* as the business
write:

```
┌─────────────────────────────┐
│          transaction          │
│  INSERT order                │
│  INSERT outbox_entries row   │
└─────────────────────────────┘
          commits atomically
                 │
                 v
      ┌───────────────────┐
      │   relay (separate   │
      │   process) polls    │
      │   outbox_entries    │
      └───────────────────┘
                 │
                 v
         publish to broker
```

A separate relay process polls that table and does the actual publishing,
with retries and deduplication handled entirely on the relay side —
decoupled from the request path. See [guarantees.md](guarantees.md) for the
exact delivery semantics this gives you.
