# Contributing

## Setup

```bash
pip install -e ".[dev]"
```

## Running checks locally

```bash
ruff check src tests
mypy src
pytest -v
```

Integration tests for a specific broker (e.g. `tests/backends/test_kafka.py`)
are skipped unless that broker's environment variable is set. You can bring
up local infra with `docker compose -f examples/docker-compose.yml up`.

## Adding a backend

See [docs/backends.md](docs/backends.md) for the `Backend` protocol and
guidelines for a new adapter.

## Pull requests

- Keep the core (`outbox.py`, `relay.py`, `dedup.py`, `models.py`) free of
  any specific broker's SDK dependency.
- Add or update tests for any behavior change, and update
  [CHANGELOG.md](CHANGELOG.md) under `[Unreleased]`.
