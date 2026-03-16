from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Union
from uuid import UUID

from .models import NeonDate, NeonDateTime, NeonDuration, NeonTime, NeonUUID, NeonValue
from .serializer import _decimal_to_str

NormalizedValue = Union[
    None,
    bool,
    int,
    float,
    str,
    list["NormalizedValue"],
    dict[str, "NormalizedValue"],
]


def normalize(value: NeonValue) -> NormalizedValue:
    if value is None or isinstance(value, (bool, int, str)):
        return value

    if isinstance(value, Decimal):
        return {"$decimal": _decimal_to_str(value)}

    if isinstance(value, NeonDate):
        return {"$tag": "date", "value": value.value.isoformat()}
    if isinstance(value, NeonDateTime):
        return {"$tag": "datetime", "value": value.value.isoformat()}
    if isinstance(value, NeonTime):
        return {"$tag": "time", "value": value.value.isoformat()}
    if isinstance(value, NeonDuration):
        return {"$tag": "duration", "value": value.canonical()}
    if isinstance(value, NeonUUID):
        return {"$tag": "uuid", "value": str(value.value)}

    if isinstance(value, date) and not isinstance(value, datetime):
        return {"$tag": "date", "value": value.isoformat()}
    if isinstance(value, datetime):
        return {"$tag": "datetime", "value": value.isoformat()}
    if isinstance(value, time):
        return {"$tag": "time", "value": value.isoformat()}
    if isinstance(value, UUID):
        return {"$tag": "uuid", "value": str(value)}

    if isinstance(value, list):
        return [normalize(v) for v in value]

    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}

    raise TypeError(f"Cannot normalize value of type {type(value).__name__}")
