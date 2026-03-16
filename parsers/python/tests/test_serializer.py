from __future__ import annotations

from neon import dumps, format_text, loads


def test_dumps_pretty_and_compact() -> None:
    value = {"a": 1, "b": [1, 2, 3]}
    pretty = dumps(value, mode="pretty")
    compact = dumps(value, mode="compact")

    assert "\n" in pretty
    assert compact == '{"a":1,"b":[1,2,3]}'


def test_format_is_idempotent() -> None:
    src = '{"a":1,"b":[1,2,3],}'
    once = format_text(src)
    twice = format_text(once)
    assert once == twice


def test_env_is_not_serialized_back_as_tag() -> None:
    src = '{"host": @env(NEON_TEST_HOST, "localhost")}'
    out = dumps(loads(src), mode="pretty")
    assert "@env" not in out
    assert "localhost" in out
