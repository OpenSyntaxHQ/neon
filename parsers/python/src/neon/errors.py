from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ErrorSpan:
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None


class NeonError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        line: int,
        column: int,
        *,
        end_line: int | None = None,
        end_column: int | None = None,
    ) -> None:
        super().__init__(f"{code}: {message} (line {line}, column {column})")
        self.code = code
        self.message = message
        self.line = line
        self.column = column
        self.end_line = end_line
        self.end_column = end_column

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
        }
        if self.end_line is not None:
            payload["end_line"] = self.end_line
        if self.end_column is not None:
            payload["end_column"] = self.end_column
        return payload


class LexError(NeonError):
    pass


class NeonSyntaxError(NeonError):
    pass


class SemanticError(NeonError):
    pass


class EnvError(NeonError):
    pass
