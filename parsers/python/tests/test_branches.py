from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

import pytest

from neon import dumps, loads
from neon.ast import Node
from neon.errors import LexError, SemanticError
from neon.lexer import tokenize
from neon.normalize import normalize
from neon.resolver import resolve


def test_invalid_mode_rejected() -> None:
    with pytest.raises(SemanticError) as exc:
        loads('{"a": 1}', mode="invalid")
    assert exc.value.code == "E_SEM_INVALID_MODE"


def test_unknown_tag_fails() -> None:
    with pytest.raises(SemanticError) as exc:
        loads('{"a": @unknown("x")}')
    assert exc.value.code == "E_SEM_UNKNOWN_TAG"


def test_invalid_duration_zero_fails() -> None:
    with pytest.raises(SemanticError) as exc:
        loads('{"a": @duration("0s")}')
    assert exc.value.code == "E_SEM_INVALID_TAG_ARG"


def test_env_default_non_string_fails() -> None:
    with pytest.raises(SemanticError) as exc:
        loads('{"a": @env(DB_HOST, 123)}')
    assert exc.value.code == "E_SEM_INVALID_TAG_ARG"


def test_env_reads_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEON_ENV_TEST", "prod-db")
    value = loads('{"a": @env(NEON_ENV_TEST)}')
    assert value["a"] == "prod-db"


def test_resolve_unknown_node_type() -> None:
    node = Node(line=1, column=1, end_line=1, end_column=1)
    with pytest.raises(SemanticError) as exc:
        resolve(node)
    assert exc.value.code == "E_SEM_UNKNOWN_NODE"


def test_serializer_invalid_mode_and_unserializable_type() -> None:
    with pytest.raises(SemanticError) as exc:
        dumps({"a": 1}, mode="bad")
    assert exc.value.code == "E_SEM_INVALID_MODE"

    class Unknown:
        pass

    with pytest.raises(SemanticError) as exc:
        dumps(Unknown())  # type: ignore[arg-type]
    assert exc.value.code == "E_SEM_UNSERIALIZABLE_TYPE"


def test_serializer_handles_native_taggable_types() -> None:
    payload = {
        "d": date(2026, 3, 16),
        "dt": datetime.fromisoformat("2026-03-16T10:30:00"),
        "t": time.fromisoformat("10:30:00"),
        "u": UUID("550e8400-e29b-41d4-a716-446655440000"),
        "x": Decimal("-0"),
    }
    out = dumps(payload, mode="compact")
    assert '@date("2026-03-16")' in out
    assert '@datetime("2026-03-16T10:30:00")' in out
    assert '@time("10:30:00")' in out
    assert '@uuid("550e8400-e29b-41d4-a716-446655440000")' in out
    assert '"x":0' in out


def test_serializer_validates_object_keys() -> None:
    with pytest.raises(SemanticError) as exc:
        dumps({1: "x"})  # type: ignore[arg-type]
    assert exc.value.code == "E_SEM_UNSERIALIZABLE_TYPE"


def test_normalize_native_types_and_error() -> None:
    value = {
        "d": date(2026, 3, 16),
        "dt": datetime.fromisoformat("2026-03-16T10:30:00"),
        "t": time.fromisoformat("10:30:00"),
        "u": UUID("550e8400-e29b-41d4-a716-446655440000"),
    }
    normalized = normalize(value)
    assert normalized["d"]["$tag"] == "date"  # type: ignore[index]
    assert normalized["dt"]["$tag"] == "datetime"  # type: ignore[index]
    assert normalized["t"]["$tag"] == "time"  # type: ignore[index]
    assert normalized["u"]["$tag"] == "uuid"  # type: ignore[index]

    with pytest.raises(TypeError):
        normalize(object())  # type: ignore[arg-type]


def test_lexer_block_comment_and_error_paths() -> None:
    tokens = tokenize('/* ok */ {"a": 1}')
    assert tokens[0].kind == "LBRACE"

    with pytest.raises(LexError) as exc:
        tokenize("/* unterminated")
    assert exc.value.code == "E_LEX_UNTERMINATED_COMMENT"

    with pytest.raises(LexError) as exc:
        tokenize('{"a": "\\u12GG"}')
    assert exc.value.code == "E_LEX_INVALID_ESCAPE"

    with pytest.raises(LexError) as exc:
        tokenize("$")
    assert exc.value.code == "E_LEX_UNEXPECTED_CHAR"
