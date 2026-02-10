from __future__ import annotations

import base64
from dataclasses import dataclass
from itertools import product
from typing import Any

import cv2
import numpy as np

from .executor import execute_pipeline
from .models import PipelineDocumentV1


@dataclass
class SweepResult:
    parameters: dict[str, Any]
    score: float
    outputs: dict[str, Any]


def _score_outputs(outputs: dict) -> float:
    """Score pipeline outputs based on image quality metrics."""
    scores: list[float] = []
    for value in outputs.values():
        # Outputs are serialized: {"mime": "image/png", "base64": "..."}
        if isinstance(value, dict) and "base64" in value:
            raw = base64.b64decode(value["base64"])
            arr = np.frombuffer(raw, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
            if img is None or img.size == 0:
                continue
            # Convert to grayscale for analysis
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img
            # Pixel variance - higher means more detail
            variance = float(np.var(gray))
            # Edge density - proportion of edge pixels
            edges = cv2.Canny(gray, 50, 150)
            edge_density = float(np.count_nonzero(edges)) / float(edges.size) if edges.size > 0 else 0.0
            # Combined score
            scores.append(variance * 0.01 + edge_density * 100.0)
    return sum(scores) / max(len(scores), 1)


def run_parameter_sweep(
    pipeline: PipelineDocumentV1,
    node_id: str,
    parameter_name: str,
    values: list[Any],
) -> list[SweepResult]:
    node = next((n for n in pipeline.nodes if n.id == node_id), None)
    if node is None:
        raise ValueError(f"Node not found: {node_id}")
    param = next((p for p in node.params if p.name == parameter_name), None)
    if param is None:
        raise ValueError(f"Parameter not found: {parameter_name}")

    results: list[SweepResult] = []
    for value in values:
        param.value = value
        run = execute_pipeline(pipeline)
        score = _score_outputs(run.outputs)
        results.append(SweepResult(parameters={parameter_name: value}, score=score, outputs=run.outputs))
    return sorted(results, key=lambda r: r.score, reverse=True)


def grid_product(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(grid.keys())
    combos = []
    for combo in product(*[grid[k] for k in keys]):
        combos.append({k: v for k, v in zip(keys, combo, strict=True)})
    return combos
