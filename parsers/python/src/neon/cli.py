from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import dumps, format_text, loads, validate
from .errors import NeonError
from .normalize import normalize


def _read_source(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _write_error(error: NeonError, *, json_errors: bool) -> None:
    if json_errors:
        sys.stderr.write(json.dumps(error.to_dict(), ensure_ascii=False) + "\n")
    else:
        sys.stderr.write(f"{error.code}: {error.message} (line {error.line}, column {error.column})\n")


def _cmd_parse(args: argparse.Namespace) -> int:
    text = _read_source(args.path)
    value = loads(text, mode=args.mode)
    payload = normalize(value)
    sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


def _cmd_format(args: argparse.Namespace) -> int:
    text = _read_source(args.path)
    if args.mode == "api":
        value = loads(text, mode="api")
        sys.stdout.write(dumps(value, mode="pretty") + "\n")
        return 0
    sys.stdout.write(format_text(text) + "\n")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    text = _read_source(args.path)
    result = validate(text, mode=args.mode)
    if args.json:
        sys.stdout.write(json.dumps({"valid": result.valid, "errors": result.errors}, ensure_ascii=False) + "\n")
    elif result.valid:
        sys.stdout.write("VALID\n")
    else:
        err = result.errors[0]
        sys.stdout.write(f"INVALID: {err['code']} - {err['message']} (line {err['line']}, column {err['column']})\n")
    return 0 if result.valid else 1


def _cmd_compact(args: argparse.Namespace) -> int:
    text = _read_source(args.path)
    value = loads(text, mode=args.mode)
    sys.stdout.write(dumps(value, mode="compact") + "\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="neon", description="NEON CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    parse_p = sub.add_parser("parse", help="Parse NEON and print normalized JSON")
    parse_p.add_argument("path", nargs="?", help="Input file path or '-' / stdin")
    parse_p.add_argument("--mode", choices=["config", "api"], default="config")
    parse_p.add_argument("--json-errors", action="store_true")
    parse_p.set_defaults(func=_cmd_parse)

    format_p = sub.add_parser("format", help="Format NEON document")
    format_p.add_argument("path", nargs="?", help="Input file path or '-' / stdin")
    format_p.add_argument("--mode", choices=["config", "api"], default="config")
    format_p.add_argument("--json-errors", action="store_true")
    format_p.set_defaults(func=_cmd_format)

    validate_p = sub.add_parser("validate", help="Validate syntax and semantics")
    validate_p.add_argument("path", nargs="?", help="Input file path or '-' / stdin")
    validate_p.add_argument("--mode", choices=["config", "api"], default="config")
    validate_p.add_argument("--json", action="store_true", help="Emit machine-readable validation output")
    validate_p.add_argument("--json-errors", action="store_true")
    validate_p.set_defaults(func=_cmd_validate)

    compact_p = sub.add_parser("compact", help="Emit compact NEON")
    compact_p.add_argument("path", nargs="?", help="Input file path or '-' / stdin")
    compact_p.add_argument("--mode", choices=["config", "api"], default="config")
    compact_p.add_argument("--json-errors", action="store_true")
    compact_p.set_defaults(func=_cmd_compact)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        func = args.func
        return int(func(args))
    except NeonError as err:
        _write_error(err, json_errors=bool(getattr(args, "json_errors", False)))
        return 1
    except FileNotFoundError as err:
        sys.stderr.write(f"E_IO_FILE_NOT_FOUND: {err}\n")
        return 2
    except OSError as err:
        sys.stderr.write(f"E_IO: {err}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
