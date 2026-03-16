# Release Checklist (1.0.0)

- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy parsers/python/src/neon`
- [ ] `pytest`
- [ ] `python scripts/validate_grammar.py`
- [ ] `python scripts/run_conformance.py`
- [ ] Verify CLI works for parse/format/validate/compact
- [ ] Review docs (README/spec/errors/CLI)
- [ ] Confirm no open P0/P1 correctness defects
- [ ] Tag and publish `1.0.0`

Post-1.0 policy: format semantics and public API changes require major versions only.
