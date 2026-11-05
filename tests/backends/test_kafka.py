"""Kafka backend tests — skipped unless a broker is available in CI."""

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("KAFKA_BOOTSTRAP_SERVERS"),
    reason="requires a running Kafka broker (set KAFKA_BOOTSTRAP_SERVERS)",
)


def test_publish_sends_to_topic():
    pytest.skip("integration test: implement once a Kafka broker is wired into CI")
