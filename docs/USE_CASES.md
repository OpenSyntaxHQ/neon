# Production Use Cases

## 1) Application Config
```neon
{
  host: @env(DB_HOST, "localhost"),
  port: 5432,
  tls: true,
}
```
- Parse in `config` mode.
- Run `neon validate` in CI before deployment.
- Run `neon format` to keep deterministic style.

## 2) API Payload Processing
- Parse incoming payload using `mode="api"`.
- `@env` is rejected by default in API mode.
- Return compact output with `neon compact` or `dumps(..., mode="compact")`.

## 3) Developer Workflow
- `neon format` + `neon validate` in pre-commit.
- Conformance tests run in CI for parser correctness.
