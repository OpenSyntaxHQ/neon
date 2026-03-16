from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY_SRC = ROOT / "parsers" / "python" / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PY_SRC) not in sys.path:
    sys.path.insert(0, str(PY_SRC))


def _main() -> int:
    from conformance.runners.python_runner import main

    return main()


if __name__ == "__main__":
    raise SystemExit(_main())
