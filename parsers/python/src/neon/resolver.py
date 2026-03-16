from __future__ import annotations

import os
import re
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from uuid import UUID

from .ast import (
    ArrayNode,
    BoolNode,
    IdentifierNode,
    Node,
    NullNode,
    NumberNode,
    ObjectNode,
    StringNode,
    TagNode,
)
from .errors import EnvError, SemanticError
from .models import NeonDate, NeonDateTime, NeonDuration, NeonTime, NeonUUID, NeonValue

_DURATION_RE = re.compile(r"^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$")


def resolve(node: Node, *, mode: str = "config", allow_env: bool | None = None) -> NeonValue:
    if mode not in {"config", "api"}:
        raise SemanticError("E_SEM_INVALID_MODE", f"Unsupported mode: {mode}", node.line, node.column)
    if allow_env is None:
        allow_env = mode == "config"
    return _resolve_node(node, allow_env=allow_env)


def _resolve_node(node: Node, *, allow_env: bool) -> NeonValue:
    if isinstance(node, ObjectNode):
        result: dict[str, NeonValue] = {}
        for pair in node.pairs:
            if pair.key in result:
                raise SemanticError(
                    "E_SEM_DUPLICATE_KEY",
                    f"Duplicate object key: {pair.key}",
                    pair.key_line,
                    pair.key_column,
                )
            result[pair.key] = _resolve_node(pair.value, allow_env=allow_env)
        return result

    if isinstance(node, ArrayNode):
        return [_resolve_node(item, allow_env=allow_env) for item in node.items]

    if isinstance(node, StringNode):
        return node.value

    if isinstance(node, NumberNode):
        return _parse_number(node)

    if isinstance(node, BoolNode):
        return node.value

    if isinstance(node, NullNode):
        return None

    if isinstance(node, IdentifierNode):
        raise SemanticError(
            "E_SEM_BARE_IDENTIFIER",
            f"Bare identifier is not a valid value: {node.name}",
            node.line,
            node.column,
            end_line=node.end_line,
            end_column=node.end_column,
        )

    if isinstance(node, TagNode):
        return _resolve_tag(node, allow_env=allow_env)

    raise SemanticError("E_SEM_UNKNOWN_NODE", "Unknown AST node", node.line, node.column)


def _parse_number(node: NumberNode) -> int | Decimal:
    raw = node.raw
    if "." in raw or "e" in raw.lower():
        try:
            return Decimal(raw)
        except InvalidOperation as exc:
            raise SemanticError("E_SEM_INVALID_NUMBER", "Invalid decimal literal", node.line, node.column) from exc
    return int(raw)


def _resolve_tag(node: TagNode, *, allow_env: bool) -> NeonValue:
    tag = node.name
    if tag == "date":
        s = _single_string_arg(node)
        try:
            return NeonDate(date.fromisoformat(s))
        except ValueError as exc:
            raise SemanticError(
                "E_SEM_INVALID_TAG_ARG", f"Invalid @date argument: {s}", node.line, node.column
            ) from exc

    if tag == "datetime":
        s = _single_string_arg(node)
        try:
            return NeonDateTime(datetime.fromisoformat(s))
        except ValueError as exc:
            raise SemanticError(
                "E_SEM_INVALID_TAG_ARG", f"Invalid @datetime argument: {s}", node.line, node.column
            ) from exc

    if tag == "time":
        s = _single_string_arg(node)
        try:
            return NeonTime(time.fromisoformat(s))
        except ValueError as exc:
            raise SemanticError(
                "E_SEM_INVALID_TAG_ARG", f"Invalid @time argument: {s}", node.line, node.column
            ) from exc

    if tag == "duration":
        s = _single_string_arg(node)
        m = _DURATION_RE.fullmatch(s)
        if not m:
            raise SemanticError("E_SEM_INVALID_TAG_ARG", f"Invalid @duration argument: {s}", node.line, node.column)
        hours = int(m.group(1) or "0")
        minutes = int(m.group(2) or "0")
        seconds = int(m.group(3) or "0")
        if hours == 0 and minutes == 0 and seconds == 0:
            raise SemanticError(
                "E_SEM_INVALID_TAG_ARG",
                "@duration must contain at least one non-zero component",
                node.line,
                node.column,
            )
        return NeonDuration(hours=hours, minutes=minutes, seconds=seconds, raw=s)

    if tag == "uuid":
        s = _single_string_arg(node)
        try:
            return NeonUUID(UUID(s))
        except ValueError as exc:
            raise SemanticError(
                "E_SEM_INVALID_TAG_ARG", f"Invalid @uuid argument: {s}", node.line, node.column
            ) from exc

    if tag == "env":
        return _resolve_env_tag(node, allow_env=allow_env)

    raise SemanticError("E_SEM_UNKNOWN_TAG", f"Unknown tag @{tag}", node.line, node.column)


def _single_string_arg(node: TagNode) -> str:
    if len(node.args) != 1:
        raise SemanticError(
            "E_SEM_INVALID_TAG_ARG",
            f"@{node.name} expects exactly 1 argument",
            node.line,
            node.column,
        )
    arg = node.args[0]
    if isinstance(arg, StringNode):
        return arg.value
    if isinstance(arg, IdentifierNode):
        return arg.name
    raise SemanticError(
        "E_SEM_INVALID_TAG_ARG",
        f"@{node.name} argument must be a string",
        arg.line,
        arg.column,
    )


def _resolve_env_tag(node: TagNode, *, allow_env: bool) -> str:
    if not allow_env:
        raise EnvError("E_ENV_NOT_ALLOWED", "@env is not allowed in this mode", node.line, node.column)

    if len(node.args) not in {1, 2}:
        raise SemanticError("E_SEM_INVALID_TAG_ARG", "@env expects 1 or 2 arguments", node.line, node.column)

    first = node.args[0]
    if isinstance(first, IdentifierNode):
        var_name = first.name
    elif isinstance(first, StringNode):
        var_name = first.value
    else:
        raise SemanticError(
            "E_SEM_INVALID_TAG_ARG", "@env first argument must be identifier or string", first.line, first.column
        )

    default: str | None = None
    if len(node.args) == 2:
        second = node.args[1]
        if isinstance(second, StringNode):
            default = second.value
        else:
            raise SemanticError("E_SEM_INVALID_TAG_ARG", "@env default must be a string", second.line, second.column)

    current = os.getenv(var_name)
    if current is not None:
        return current
    if default is not None:
        return default

    raise EnvError(
        "E_ENV_MISSING",
        f"Environment variable '{var_name}' is not set and no default was provided",
        node.line,
        node.column,
    )
