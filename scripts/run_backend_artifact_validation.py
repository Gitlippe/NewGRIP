#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "pipelines"
ARTIFACT_DIR = ROOT / ".artifacts" / "verification"
IMAGE_PATH = ROOT / "examples" / "assets" / "web-test-image.jpg"
API_BASE = "http://127.0.0.1:8000"
MAX_RETRIES = 10
RETRY_DELAY = 2


def post_json(path: str, payload: dict, *, retries: int = 0) -> dict:
    req = Request(
        f"{API_BASE}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(retries + 1):
        try:
            with urlopen(req) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except (URLError, ConnectionError) as exc:
            if attempt < retries:
                print(f"  Retry {attempt + 1}/{retries} for {path}: {exc}")
                time.sleep(RETRY_DELAY)
            else:
                raise


def hash_output(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    report: dict = {"pipelines": []}

    first = True
    for fixture in sorted(FIXTURE_DIR.glob("*.json")):
        pipeline = json.loads(fixture.read_text(encoding="utf-8"))
        validate = post_json(
            "/v1/pipelines/validate",
            {"pipeline": pipeline},
            retries=MAX_RETRIES if first else 0,
        )
        first = False
        run = post_json(
            "/v1/pipelines/run",
            {"pipeline": pipeline, "inputImagePath": str(IMAGE_PATH)},
        )
        output_hashes = {k: hash_output(v) for k, v in run.get("outputs", {}).items()}

        report["pipelines"].append(
            {
                "fixture": fixture.name,
                "validate_ok": validate.get("ok", False),
                "run_ok": run.get("ok", False),
                "trace_count": len(run.get("traces", [])),
                "output_keys": sorted(run.get("outputs", {}).keys()),
                "output_hashes": output_hashes,
                "artifact_count": len(run.get("artifacts", [])),
            }
        )

    report_path = ARTIFACT_DIR / "backend-artifact-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(str(report_path))

    # Assert correctness and gate on failures
    failures = []
    for entry in report["pipelines"]:
        name = entry["fixture"]
        if not entry["validate_ok"]:
            failures.append(f"{name}: validation failed")
        if not entry["run_ok"]:
            failures.append(f"{name}: run failed")
        if not entry["output_keys"]:
            failures.append(f"{name}: no outputs produced")

    total = len(report["pipelines"])
    passed = total - len(failures)
    print(f"\n{passed}/{total} pipelines passed")
    if failures:
        for f in failures:
            print(f"  FAIL: {f}")
        raise SystemExit(1)
    print("All pipelines passed validation and execution.")


if __name__ == "__main__":
    main()
