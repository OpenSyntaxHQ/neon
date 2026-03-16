# NEON 1.0 Specification

## 1. Scope
NEON 1.0 is a textual data format for configuration and API payloads.

## 2. Data Model
Supported values:
- Object
- Array
- String
- Number
- Boolean
- Null
- Tagged values: `@date`, `@datetime`, `@time`, `@duration`, `@uuid`, `@env`

## 3. Syntax Rules
- Objects use `{ ... }`.
- Arrays use `[ ... ]`.
- Object keys can be quoted strings or bare identifiers.
- Comments are allowed:
  - line: `# comment`
  - line: `// comment`
  - block: `/* comment */`
- Trailing commas are allowed in objects and arrays.

## 4. Numbers
- Integers: JSON-style integer literals.
- Decimals: JSON-style decimal/exponent literals.
- Runtime canonicalization:
  - integer literals -> Python `int`
  - decimal/exponent literals -> Python `Decimal`

## 5. Tag Semantics
- `@date("YYYY-MM-DD")` -> `NeonDate`
- `@datetime("ISO-8601 datetime")` -> `NeonDateTime`
- `@time("HH:MM[:SS[.ffffff]][+TZ]")` -> `NeonTime`
- `@duration("1h30m15s")` -> `NeonDuration`
- `@uuid("uuid-string")` -> `NeonUUID`
- `@env(VAR)` / `@env(VAR, "default")` -> resolved `str`

Tag validation is strict:
- unknown tags are invalid
- wrong argument count/type is invalid
- malformed tag values are invalid

## 6. Mode Semantics
- `config` mode: `@env` allowed.
- `api` mode: `@env` rejected by default.
- Serializer never emits unresolved `@env`; resolved string is emitted.

## 7. Deterministic Serialization
- `pretty` mode: indented, stable formatting.
- `compact` mode: no unnecessary whitespace.
- Serializer output must be deterministic for a given input value.

## 8. Error Model
All errors include code, message, line, and column.

Code families:
- Lexical: `E_LEX_*`
- Syntax: `E_SYN_*`
- Semantic: `E_SEM_*`
- Environment: `E_ENV_*`

Core codes:
- `E_LEX_UNEXPECTED_CHAR`
- `E_LEX_UNTERMINATED_STRING`
- `E_LEX_INVALID_ESCAPE`
- `E_LEX_UNTERMINATED_COMMENT`
- `E_SYN_EXPECTED_VALUE`
- `E_SYN_EXPECTED_TOKEN`
- `E_SYN_TRAILING_TOKENS`
- `E_SEM_DUPLICATE_KEY`
- `E_SEM_UNKNOWN_TAG`
- `E_SEM_INVALID_TAG_ARG`
- `E_SEM_BARE_IDENTIFIER`
- `E_SEM_UNSERIALIZABLE_TYPE`
- `E_ENV_NOT_ALLOWED`
- `E_ENV_MISSING`

## 9. Conformance
Conformance inputs are split into:
- `conformance/valid`: must parse and match normalized expected output.
- `conformance/invalid`: must fail with expected error code/location.

The conformance suite is required for release.
