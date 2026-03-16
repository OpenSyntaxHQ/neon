from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from neon import loads
from neon.errors import NeonError
from neon.normalize import normalize


@dataclass
class Failure:
    case: str
    reason: str


@dataclass
class Summary:
    total: int
    passed: int
    failed: int
    failures: list[Failure]

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "failures": [{"case": f.case, "reason": f.reason} for f in self.failures],
        }


@contextmanager
def _patched_env(overrides: dict[str, str | None] | None) -> Iterator[None]:
    if not overrides:
        yield
        return

    original: dict[str, str | None] = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _load_options(case_dir: Path) -> dict[str, object]:
    options_path = case_dir / "options.json"
    if not options_path.exists():
        return {}
    return json.loads(options_path.read_text(encoding="utf-8"))


def _run_valid_case(case_dir: Path) -> Failure | None:
    source = (case_dir / "input.neon").read_text(encoding="utf-8")
    expected = json.loads((case_dir / "expected.json").read_text(encoding="utf-8"))
    options = _load_options(case_dir)
    mode = str(options.get("mode", "config"))
    env = options.get("env")
    env_map = env if isinstance(env, dict) else None

    try:
        with _patched_env(env_map):
            actual = normalize(loads(source, mode=mode))
    except NeonError as err:
        return Failure(case=case_dir.name, reason=f"Expected valid, got error {err.code}")

    if actual != expected:
        return Failure(case=case_dir.name, reason=f"Output mismatch. actual={actual} expected={expected}")
    return None


def _run_invalid_case(case_dir: Path) -> Failure | None:
    source = (case_dir / "input.neon").read_text(encoding="utf-8")
    expected = json.loads((case_dir / "error.json").read_text(encoding="utf-8"))
    options = _load_options(case_dir)
    mode = str(options.get("mode", "config"))
    env = options.get("env")
    env_map = env if isinstance(env, dict) else None

    try:
        with _patched_env(env_map):
            loads(source, mode=mode)
    except NeonError as err:
        if err.code != expected.get("code"):
            return Failure(
                case=case_dir.name,
                reason=f"Error code mismatch. actual={err.code} expected={expected.get('code')}",
            )
        if "line" in expected and int(expected["line"]) != err.line:
            return Failure(case=case_dir.name, reason=f"Line mismatch. actual={err.line} expected={expected['line']}")
        if "column" in expected and int(expected["column"]) != err.column:
            return Failure(
                case=case_dir.name,
                reason=f"Column mismatch. actual={err.column} expected={expected['column']}",
            )
        return None

    return Failure(case=case_dir.name, reason="Expected invalid case to fail, but it passed")


def run_conformance(base_dir: Path) -> Summary:
    failures: list[Failure] = []

    valid_dirs = sorted(p for p in (base_dir / "valid").iterdir() if p.is_dir())
    invalid_dirs = sorted(p for p in (base_dir / "invalid").iterdir() if p.is_dir())

    for case_dir in valid_dirs:
        failure = _run_valid_case(case_dir)
        if failure is not None:
            failures.append(failure)

    for case_dir in invalid_dirs:
        failure = _run_invalid_case(case_dir)
        if failure is not None:
            failures.append(failure)

    total = len(valid_dirs) + len(invalid_dirs)
    failed = len(failures)
    passed = total - failed
    return Summary(total=total, passed=passed, failed=failed, failures=failures)


def main() -> int:
    base_dir = Path(__file__).resolve().parents[1]
    summary = run_conformance(base_dir)
    print(json.dumps(summary.to_dict(), indent=2))
    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
