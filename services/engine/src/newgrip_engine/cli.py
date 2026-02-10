from __future__ import annotations

import argparse
import json
from pathlib import Path

from .codegen import generate_code
from .executor import execute_pipeline
from .models import PipelineDocumentV1
from .parity import run_parity_scan
from .persistence import load_newgrip
from .validator import validate_pipeline


def _load_pipeline(path: str) -> PipelineDocumentV1:
    p = Path(path)
    if p.suffix == ".json":
        return load_newgrip(p)
    return PipelineDocumentV1.model_validate(json.loads(p.read_text(encoding="utf-8")))


def cmd_validate(args: argparse.Namespace) -> int:
    pipeline = _load_pipeline(args.pipeline)
    result = validate_pipeline(pipeline)
    print(json.dumps(result.model_dump(), indent=2))
    return 0 if result.ok else 1


def cmd_run(args: argparse.Namespace) -> int:
    pipeline = _load_pipeline(args.pipeline)
    result = execute_pipeline(pipeline, args.input, args.artifacts_dir)
    print(json.dumps(result.model_dump(), indent=2))
    return 0 if result.ok else 1


def cmd_export(args: argparse.Namespace) -> int:
    pipeline = _load_pipeline(args.pipeline)
    filename, content = generate_code(pipeline, args.language, args.class_name)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / filename
    target.write_text(content, encoding="utf-8")
    print(str(target))
    return 0


def cmd_parity(args: argparse.Namespace) -> int:
    results = run_parity_scan(Path(args.grip_samples_dir))
    print(json.dumps([r.__dict__ for r in results], indent=2))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="newgrip")
    sub = parser.add_subparsers(required=True)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--pipeline", required=True)
    p_validate.set_defaults(func=cmd_validate)

    p_run = sub.add_parser("run")
    p_run.add_argument("--pipeline", required=True)
    p_run.add_argument("--input")
    p_run.add_argument("--artifacts-dir")
    p_run.set_defaults(func=cmd_run)

    p_export = sub.add_parser("export")
    p_export.add_argument("--pipeline", required=True)
    p_export.add_argument("--language", required=True, choices=["python", "java", "cpp"])
    p_export.add_argument("--class-name", default="GeneratedPipeline")
    p_export.add_argument("--output-dir", default=".")
    p_export.set_defaults(func=cmd_export)

    p_parity = sub.add_parser("parity")
    p_parity.add_argument("--grip-samples-dir", required=True)
    p_parity.set_defaults(func=cmd_parity)

    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
