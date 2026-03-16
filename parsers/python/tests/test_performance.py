from __future__ import annotations

import time

import pytest

from neon import dumps, loads


@pytest.mark.perf
def test_parse_and_serialize_performance_budget() -> None:
    items = ",".join(f'{{"id": {i}, "name": "service-{i}", "ok": true}}' for i in range(600))
    doc = "{" + f'"services": [{items}], "meta": {{"region": "ap-south-1"}}' + "}"

    start = time.perf_counter()
    value = loads(doc)
    parse_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    dumps(value, mode="compact")
    serialize_elapsed = time.perf_counter() - start

    assert parse_elapsed < 1.5
    assert serialize_elapsed < 1.5
