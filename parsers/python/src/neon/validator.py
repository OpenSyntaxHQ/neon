from __future__ import annotations

from .errors import NeonError
from .models import ValidationResult


def make_valid_result() -> ValidationResult:
    return ValidationResult(valid=True, errors=[])


def make_invalid_result(error: NeonError) -> ValidationResult:
    return ValidationResult(valid=False, errors=[error.to_dict()])
