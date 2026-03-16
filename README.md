# NEON (Next Exchange Object Notation)

NEON is a human-readable data format for configs and API payloads.

## Status
- Reference implementation: Python 3.9+
- CI tested versions: Python 3.10, 3.11, 3.12, 3.13
- Release policy: first public release after all CI quality gates pass
- Current scope: parser, serializer, CLI, conformance suite

## Install (local dev)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e "parsers/python[dev]"
```

## Quick Start
```python
from neon import loads, dumps, format_text

doc = '{"host": @env(DB_HOST, "localhost"), "retry": 3}'
value = loads(doc, mode="config")
print(value)
print(dumps(value, mode="pretty"))
print(format_text(doc))
```

## CLI
```bash
neon parse config.neon
neon format config.neon
neon validate config.neon
neon compact config.neon
```

Use stdin by omitting file path:
```bash
cat config.neon | neon validate
```

## Repository Layout
- `spec/`: NEON 1.0 specification and grammar
- `conformance/`: language-agnostic test corpus and runner
- `parsers/python/`: reference implementation
- `scripts/`: CI helper scripts
- `docs/`: operational and user docs

