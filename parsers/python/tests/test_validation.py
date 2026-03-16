from __future__ import annotations

from neon import validate


def test_validate_success() -> None:
    result = validate('{"a": 1}')
    assert result.valid is True
    assert result.errors == []


def test_validate_failure() -> None:
    result = validate('{"a": }')
    assert result.valid is False
    assert result.errors
    assert result.errors[0]["code"].startswith("E_")
