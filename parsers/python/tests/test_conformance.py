from __future__ import annotations

from pathlib import Path

from conformance.runners.python_runner import run_conformance


def test_conformance_suite_passes() -> None:
    base = Path(__file__).resolve().parents[3] / "conformance"
    summary = run_conformance(base)
    assert summary.failed == 0, summary.to_dict()
