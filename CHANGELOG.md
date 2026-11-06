# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- `README.md` architecture diagrams (ASCII and Mermaid) and a
  `docs/quickstart.md` walkthrough.
- PyPI classifiers and keywords in `pyproject.toml`.
- Delivery-error handling in `KafkaBackend` (raises `KafkaDeliveryError` on
  a failed delivery or pending messages after flush).

### Changed

- CI now installs the `kafka`/`redis`/`sqs` extras and runs `mypy` and
  coverage reporting across both `src` and `tests`.

## [0.1.0] - 2026-11-05

### Added

- Initial project scaffold: `Outbox` (write side), `Relay` (read side),
  `DeliveryTracker` (dedup), and `Backend` protocol.
- Built-in backends: in-memory, Kafka, Redis Streams, SQS.
- Chaos test for crash/recovery semantics.
- Docs: the dual-write problem, delivery guarantees, writing a backend.
- FastAPI order-service example.
