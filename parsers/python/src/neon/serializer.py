from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from .errors import SemanticError
from .models import NeonDate, NeonDateTime, NeonDuration, NeonTime, NeonUUID, NeonValue


def dumps_value(value: NeonValue, *, mode: str = "pretty") -> str:
    if mode not in {"pretty", "compact"}:
        raise SemanticError("E_SEM_INVALID_MODE", f"Unsupported dump mode: {mode}", 1, 1)
    return _serialize(value, compact=mode == "compact", depth=0)


def _serialize(value: NeonValue, *, compact: bool, depth: int) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Decimal):
        return _decimal_to_str(value)
    if isinstance(value, str):
        return _quote(value)

    if isinstance(value, NeonDate):
        return f"@date({_quote(value.value.isoformat())})"
    if isinstance(value, NeonDateTime):
        return f"@datetime({_quote(value.value.isoformat())})"
    if isinstance(value, NeonTime):
        return f"@time({_quote(value.value.isoformat())})"
    if isinstance(value, NeonDuration):
        return f"@duration({_quote(value.canonical())})"
    if isinstance(value, NeonUUID):
        return f"@uuid({_quote(str(value.value))})"

    if isinstance(value, date) and not isinstance(value, datetime):
        return f"@date({_quote(value.isoformat())})"
    if isinstance(value, datetime):
        return f"@datetime({_quote(value.isoformat())})"
    if isinstance(value, time):
        return f"@time({_quote(value.isoformat())})"
    if isinstance(value, UUID):
        return f"@uuid({_quote(str(value))})"

    if isinstance(value, list):
        return _serialize_list(value, compact=compact, depth=depth)
    if isinstance(value, dict):
        return _serialize_object(value, compact=compact, depth=depth)

    raise SemanticError(
        "E_SEM_UNSERIALIZABLE_TYPE",
        f"Value of type {type(value).__name__} is not serializable",
        1,
        1,
    )


def _serialize_list(values: list[NeonValue], *, compact: bool, depth: int) -> str:
    if not values:
        return "[]"
    if compact:
        return "[" + ",".join(_serialize(v, compact=True, depth=depth + 1) for v in values) + "]"

    indent = "  " * depth
    child_indent = "  " * (depth + 1)
    pieces = [child_indent + _serialize(v, compact=False, depth=depth + 1) for v in values]
    return "[\n" + ",\n".join(pieces) + "\n" + indent + "]"


def _serialize_object(values: dict[str, NeonValue], *, compact: bool, depth: int) -> str:
    if not values:
        return "{}"
    for key in values:
        if not isinstance(key, str):
            raise SemanticError("E_SEM_UNSERIALIZABLE_TYPE", "Object keys must be strings", 1, 1)

    items = list(values.items())
    if compact:
        inner = ",".join(f"{_quote(k)}:{_serialize(v, compact=True, depth=depth + 1)}" for k, v in items)
        return "{" + inner + "}"

    indent = "  " * depth
    child_indent = "  " * (depth + 1)
    rendered = [f"{child_indent}{_quote(k)}: {_serialize(v, compact=False, depth=depth + 1)}" for k, v in items]
    return "{\n" + ",\n".join(rendered) + "\n" + indent + "}"


def _quote(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\b", "\\b")
        .replace("\f", "\\f")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'


def _decimal_to_str(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        return "0"
    return text
