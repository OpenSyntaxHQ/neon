from __future__ import annotations

from neon.compact import compact


def test_compact_helper() -> None:
    out = compact({"a": 1, "b": [1, 2]})
    assert out == '{"a":1,"b":[1,2]}'
