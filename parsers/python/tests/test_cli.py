from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from neon import cli

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parents[1] / "src"


def _run_cli(args: list[str], stdin: str = "") -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    return subprocess.run(
        [sys.executable, "-m", "neon.cli", *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
        check=False,
    )


def test_cli_parse_from_stdin_subprocess() -> None:
    proc = _run_cli(["parse"], stdin='{"a": 1}')
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["a"] == 1


def test_cli_validate_invalid_document_subprocess() -> None:
    proc = _run_cli(["validate", "--json"], stdin='{"a": }')
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["valid"] is False


def test_cli_compact_output_subprocess() -> None:
    proc = _run_cli(["compact"], stdin='{"a": 1, "b": [1,2,3]}')
    assert proc.returncode == 0
    assert proc.stdout.strip() == '{"a":1,"b":[1,2,3]}'


def test_cli_parse_from_stdin_inprocess(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"a": 1}'))
    code = cli.main(["parse"])
    captured = capsys.readouterr()
    assert code == 0
    assert json.loads(captured.out)["a"] == 1


def test_cli_validate_json_inprocess(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"a": }'))
    code = cli.main(["validate", "--json"])
    captured = capsys.readouterr()
    assert code == 1
    assert json.loads(captured.out)["valid"] is False


def test_cli_json_errors_inprocess(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"a": }'))
    code = cli.main(["parse", "--json-errors"])
    captured = capsys.readouterr()
    assert code == 1
    payload = json.loads(captured.err)
    assert payload["code"].startswith("E_")


def test_cli_missing_file_returns_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    code = cli.main(["parse", "missing-file.neon"])
    captured = capsys.readouterr()
    assert code == 2
    assert "E_IO_FILE_NOT_FOUND" in captured.err


def test_cli_help_exit_code_2() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.build_parser().parse_args([])
    assert exc.value.code == 2


def test_cli_format_and_compact_from_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "doc.neon"
    path.write_text('{"a": 1, "b": [1,2,3]}', encoding="utf-8")

    code = cli.main(["format", str(path)])
    captured = capsys.readouterr()
    assert code == 0
    assert '"a": 1' in captured.out

    code = cli.main(["compact", str(path)])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip() == '{"a":1,"b":[1,2,3]}'


def test_cli_format_api_mode(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"a": 1}'))
    code = cli.main(["format", "--mode", "api"])
    captured = capsys.readouterr()
    assert code == 0
    assert '"a": 1' in captured.out


def test_cli_handles_oserror(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli, "_read_source", lambda _: (_ for _ in ()).throw(OSError("disk failure")))
    code = cli.main(["parse"])
    captured = capsys.readouterr()
    assert code == 2
    assert "E_IO:" in captured.err
