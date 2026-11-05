# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- Initial project scaffold: `Outbox` (write side), `Relay` (read side),
  `DeliveryTracker` (dedup), and `Backend` protocol.
- Built-in backends: in-memory, Kafka, Redis Streams, SQS.
- Chaos test for crash/recovery semantics.
- Docs: the dual-write problem, delivery guarantees, writing a backend.
- FastAPI order-service example.
