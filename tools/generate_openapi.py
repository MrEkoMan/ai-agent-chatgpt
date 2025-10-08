
import json
import sys
from pathlib import Path

# Ensure the project root is on sys.path so we can import the FastAPI app
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api import app  # noqa: E402


def main() -> None:
    out = ROOT / "openapi.json"
    data = app.openapi()
    out.write_text(json.dumps(data, indent=2))
    print(f"Wrote OpenAPI JSON to {out}")


if __name__ == "__main__":
    main()
