from __future__ import annotations

import json
import time

from neon import dumps, loads


def _benchmark_case(doc: str) -> dict[str, float]:
    start = time.perf_counter()
    value = loads(doc)
    parse_s = time.perf_counter() - start

    start = time.perf_counter()
    dumps(value, mode="compact")
    serialize_s = time.perf_counter() - start

    return {"parse_s": parse_s, "serialize_s": serialize_s}


def main() -> int:
    small = '{"a": 1, "b": [1,2,3], "c": @date("2026-03-16")}'
    medium_items = ",".join(f'{{"id": {i}, "name": "svc-{i}"}}' for i in range(200))
    medium = "{" + f'"services": [{medium_items}]' + "}"
    large_items = ",".join(f'{{"id": {i}, "ok": true, "ratio": 1.25}}' for i in range(1500))
    large = "{" + f'"records": [{large_items}]' + "}"

    report = {
        "small": _benchmark_case(small),
        "medium": _benchmark_case(medium),
        "large": _benchmark_case(large),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
