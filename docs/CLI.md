# CLI Reference

## Commands
- `neon parse [path] [--mode config|api]`
- `neon format [path] [--mode config|api]`
- `neon validate [path] [--mode config|api] [--json]`
- `neon compact [path] [--mode config|api]`

If path is omitted or set to `-`, input is read from stdin.

## Exit Codes
- `0`: success
- `1`: parse/semantic validation failure
- `2`: usage or IO failure

## Machine-Readable Errors
Add `--json-errors` to commands to emit JSON error payloads on stderr.
