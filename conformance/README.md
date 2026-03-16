# NEON Conformance Suite

## Layout
- `valid/*/input.neon`: document that must parse.
- `valid/*/expected.json`: normalized output value.
- `invalid/*/input.neon`: document that must fail.
- `invalid/*/error.json`: expected error code and location.

## Normalized Value Contract
- `Decimal` -> `{ "$decimal": "<canonical>" }`
- `NeonDate` -> `{ "$tag": "date", "value": "YYYY-MM-DD" }`
- `NeonDateTime` -> `{ "$tag": "datetime", "value": "..." }`
- `NeonTime` -> `{ "$tag": "time", "value": "..." }`
- `NeonDuration` -> `{ "$tag": "duration", "value": "..." }`
- `NeonUUID` -> `{ "$tag": "uuid", "value": "..." }`

## Runner
`conformance/runners/python_runner.py` reads this corpus and validates parsing behavior.
