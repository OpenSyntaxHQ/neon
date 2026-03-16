from __future__ import annotations

from pathlib import Path

REQUIRED_RULES = {
    "document",
    "value",
    "object",
    "array",
    "tag",
    "number",
    "string",
    "identifier",
}


def main() -> int:
    grammar_path = Path("spec/grammar.ebnf")
    if not grammar_path.exists():
        print("E_SPEC_GRAMMAR_MISSING: spec/grammar.ebnf not found")
        return 1

    content = grammar_path.read_text(encoding="utf-8")
    missing = sorted(rule for rule in REQUIRED_RULES if f"{rule}" not in content)
    if missing:
        print(f"E_SPEC_GRAMMAR_INVALID: Missing required productions: {', '.join(missing)}")
        return 1

    if "document" not in content.splitlines()[0]:
        print("E_SPEC_GRAMMAR_INVALID: First production should define document")
        return 1

    print("Grammar validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
