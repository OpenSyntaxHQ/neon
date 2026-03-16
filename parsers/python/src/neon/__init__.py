from __future__ import annotations

from typing import Literal

from .errors import EnvError, LexError, NeonError, NeonSyntaxError, SemanticError
from .models import (
    NeonDate,
    NeonDateTime,
    NeonDuration,
    NeonTime,
    NeonUUID,
    NeonValue,
    ValidationResult,
)
from .parser import parse_text
from .resolver import resolve
from .serializer import dumps_value
from .validator import make_invalid_result, make_valid_result

__all__ = [
    "EnvError",
    "LexError",
    "NeonDate",
    "NeonDateTime",
    "NeonDuration",
    "NeonError",
    "NeonSyntaxError",
    "NeonTime",
    "NeonUUID",
    "NeonValue",
    "SemanticError",
    "ValidationResult",
    "dumps",
    "format_text",
    "loads",
    "validate",
]

__version__ = "1.0.0"
__spec_version__ = "1.0"


def loads(
    text: str,
    *,
    mode: Literal["config", "api"] = "config",
    allow_env: bool | None = None,
) -> NeonValue:
    ast = parse_text(text)
    return resolve(ast, mode=mode, allow_env=allow_env)


def dumps(value: NeonValue, *, mode: Literal["pretty", "compact"] = "pretty") -> str:
    return dumps_value(value, mode=mode)


def format_text(text: str) -> str:
    parsed = loads(text, mode="config")
    return dumps(parsed, mode="pretty")


def validate(text: str, *, mode: Literal["config", "api"] = "config") -> ValidationResult:
    try:
        loads(text, mode=mode)
    except NeonError as err:
        return make_invalid_result(err)
    return make_valid_result()
