from __future__ import annotations

from .models import NeonValue
from .serializer import dumps_value


def compact(value: NeonValue) -> str:
    return dumps_value(value, mode="compact")
