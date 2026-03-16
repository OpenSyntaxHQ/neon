from __future__ import annotations

import random
import string

import pytest

from neon import loads
from neon.errors import NeonError


def _random_input(rng: random.Random, length: int) -> str:
    alphabet = string.ascii_letters + string.digits + "{}[],:@()\"'#/.-_ \n\t"
    return "".join(rng.choice(alphabet) for _ in range(length))


def test_malformed_inputs_do_not_crash_parser() -> None:
    rng = random.Random(20260316)
    for _ in range(200):
        candidate = _random_input(rng, rng.randint(0, 120))
        try:
            loads(candidate)
        except NeonError:
            pass
        except Exception as exc:  # pragma: no cover
            pytest.fail(f"Unexpected non-NeonError exception: {type(exc).__name__}: {exc}")
