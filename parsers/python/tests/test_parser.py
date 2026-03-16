from __future__ import annotations

from decimal import Decimal

import pytest

from neon import loads
from neon.errors import EnvError, SemanticError
from neon.models import NeonDate, NeonDateTime, NeonDuration, NeonTime, NeonUUID


def test_loads_basic_document() -> None:
    value = loads('{"name": "neon", "count": 3, "ratio": 1.25}')
    assert value["name"] == "neon"
    assert value["count"] == 3
    assert value["ratio"] == Decimal("1.25")


def test_loads_tagged_values() -> None:
    doc = (
        '{"d": @date("2026-03-16"), "dt": @datetime("2026-03-16T10:30:00"), '
        '"t": @time("10:30:00"), "dur": @duration("1h30m"), '
        '"id": @uuid("550e8400-e29b-41d4-a716-446655440000")}'
    )
    value = loads(doc)
    assert isinstance(value["d"], NeonDate)
    assert isinstance(value["dt"], NeonDateTime)
    assert isinstance(value["t"], NeonTime)
    assert isinstance(value["dur"], NeonDuration)
    assert isinstance(value["id"], NeonUUID)


def test_duplicate_keys_fail() -> None:
    with pytest.raises(SemanticError) as exc:
        loads('{"a": 1, "a": 2}')
    assert exc.value.code == "E_SEM_DUPLICATE_KEY"


def test_env_is_blocked_in_api_mode() -> None:
    with pytest.raises(EnvError) as exc:
        loads('{"host": @env(DB_HOST, "localhost")}', mode="api")
    assert exc.value.code == "E_ENV_NOT_ALLOWED"


def test_bare_identifier_value_fails() -> None:
    with pytest.raises(SemanticError) as exc:
        loads('{"a": abc}')
    assert exc.value.code == "E_SEM_BARE_IDENTIFIER"
