from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .persistence import import_grip_xml
from .validator import validate_pipeline


@dataclass
class ParityResult:
    source: str
    converted_nodes: int
    converted_edges: int
    warnings: list[str]
    valid: bool


def run_parity_scan(grip_samples_dir: Path) -> list[ParityResult]:
    results: list[ParityResult] = []
    for sample in sorted(grip_samples_dir.glob("*.grip")):
        xml = sample.read_text(encoding="utf-8")
        pipeline, warnings = import_grip_xml(xml)
        validation = validate_pipeline(pipeline)
        results.append(
            ParityResult(
                source=sample.name,
                converted_nodes=len(pipeline.nodes),
                converted_edges=len(pipeline.edges),
                warnings=warnings,
                valid=validation.ok,
            )
        )
    return results
