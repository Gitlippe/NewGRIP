from __future__ import annotations

import base64
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np

from .models import ArtifactRef, PipelineDocumentV1, RunResponse, RunTrace
from .operations import OperationRegistry
from .validator import topological_order


def _serialize_output(value: object) -> object:
    if isinstance(value, np.ndarray):
        ok, buf = cv2.imencode(".png", value)
        if not ok:
            return None
        return {"mime": "image/png", "base64": base64.b64encode(buf.tobytes()).decode("utf-8")}
    return value


def _save_artifact(node_id: str, socket: str, value: object, run_dir: Path) -> ArtifactRef:
    if isinstance(value, np.ndarray):
        path = run_dir / f"{node_id}_{socket}.png"
        cv2.imwrite(str(path), value)
        return ArtifactRef(nodeId=node_id, socket=socket, kind="image", path=str(path))
    return ArtifactRef(nodeId=node_id, socket=socket, kind="json", value=value)


def execute_pipeline(
    pipeline: PipelineDocumentV1,
    input_image_path: str | None = None,
    artifacts_root: str | None = None,
    input_image_base64: str | None = None,
) -> RunResponse:
    order = topological_order(pipeline)
    node_map = {n.id: n for n in pipeline.nodes}
    incoming: dict[str, list] = {n.id: [] for n in pipeline.nodes}
    for edge in pipeline.edges:
        incoming[edge.to.nodeId].append(edge)

    registry = OperationRegistry()
    traces: list[RunTrace] = []
    values: dict[tuple[str, str], object] = {}
    artifacts: list[ArtifactRef] = []

    run_dir = None
    if artifacts_root:
        run_dir = Path(artifacts_root) / f"run_{uuid4().hex[:8]}"
        run_dir.mkdir(parents=True, exist_ok=True)

    # Check for fan-in conflicts (multiple edges targeting the same socket)
    for node_id in incoming:
        socket_edges: dict[tuple[str, str], list[str]] = {}
        for edge in incoming[node_id]:
            key = (edge.to.nodeId, edge.to.socket)
            socket_edges.setdefault(key, []).append(edge.id)
        for key, edge_ids in socket_edges.items():
            if len(edge_ids) > 1:
                raise ValueError(f"Fan-in conflict: socket {key[1]} on node {key[0]} has {len(edge_ids)} edges")

    for node_id in order:
        node = node_map[node_id]
        try:
            node_inputs: dict[str, object] = {}
            for edge in incoming[node_id]:
                node_inputs[edge.to.socket] = values.get((edge.from_.nodeId, edge.from_.socket))
            out = registry.run(
                node.op,
                node,
                node_inputs,
                {"inputImagePath": input_image_path, "inputImageBase64": input_image_base64},
            )
            for socket, value in out.items():
                values[(node_id, socket)] = value
                if run_dir is not None:
                    artifacts.append(_save_artifact(node_id, socket, value, run_dir))
            traces.append(RunTrace(nodeId=node_id, status="ok"))
        except Exception as exc:  # noqa: BLE001
            traces.append(RunTrace(nodeId=node_id, status="error", message=str(exc)))
            return RunResponse(ok=False, traces=traces, outputs={}, artifacts=artifacts)

    outputs: dict[str, object] = {}
    for (node_id, socket), value in values.items():
        outputs[f"{node_id}.{socket}"] = _serialize_output(value)

    return RunResponse(ok=True, traces=traces, outputs=outputs, artifacts=artifacts)
