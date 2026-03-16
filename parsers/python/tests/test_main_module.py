from __future__ import annotations

import io
import runpy
import sys

import pytest


def test_module_entrypoint_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["neon", "validate"])
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"a": 1}'))
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("neon.__main__", run_name="__main__")
    assert exc.value.code == 0
