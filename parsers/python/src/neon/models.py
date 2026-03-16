from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Union
from uuid import UUID


@dataclass(frozen=True)
class NeonDate:
    value: date


@dataclass(frozen=True)
class NeonDateTime:
    value: datetime


@dataclass(frozen=True)
class NeonTime:
    value: time


@dataclass(frozen=True)
class NeonDuration:
    hours: int
    minutes: int
    seconds: int
    raw: str

    def canonical(self) -> str:
        parts: list[str] = []
        if self.hours:
            parts.append(f"{self.hours}h")
        if self.minutes:
            parts.append(f"{self.minutes}m")
        if self.seconds:
            parts.append(f"{self.seconds}s")
        return "".join(parts) or "0s"


@dataclass(frozen=True)
class NeonUUID:
    value: UUID


NeonScalar = Union[
    None,
    bool,
    int,
    Decimal,
    str,
    NeonDate,
    NeonDateTime,
    NeonTime,
    NeonDuration,
    NeonUUID,
]
NeonValue = Union[NeonScalar, list["NeonValue"], dict[str, "NeonValue"]]


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: list[dict[str, object]]
