from __future__ import annotations

import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from .models import PipelineDocumentV1, PipelineEdge, PipelineNode, SocketSpec

GRIP_OP_MAP: dict[str, str] = {
    # Composite operations
    "edu.wpi.grip.core.operations.composite.BlurOperation": "opencv.gaussianBlur",
    "edu.wpi.grip.core.operations.composite.CannyEdgeOperation": "opencv.canny",
    "edu.wpi.grip.core.operations.composite.FindContoursOperation": "opencv.findContours",
    "edu.wpi.grip.core.operations.composite.FilterContoursOperation": "opencv.filterContours",
    "edu.wpi.grip.core.operations.composite.ConvexHullsOperation": "opencv.convexHulls",
    "edu.wpi.grip.core.operations.composite.HSVThresholdOperation": "opencv.hsvThreshold",
    "edu.wpi.grip.core.operations.composite.HSLThresholdOperation": "opencv.hslThreshold",
    "edu.wpi.grip.core.operations.composite.RGBThresholdOperation": "opencv.rgbThreshold",
    "edu.wpi.grip.core.operations.composite.DesaturateOperation": "opencv.rgbToGray",
    "edu.wpi.grip.core.operations.composite.ResizeOperation": "opencv.resize",
    "edu.wpi.grip.core.operations.composite.CropOperation": "opencv.crop",
    "edu.wpi.grip.core.operations.composite.MaskOperation": "opencv.mask",
    "edu.wpi.grip.core.operations.composite.NormalizeOperation": "opencv.normalize",
    "edu.wpi.grip.core.operations.composite.ThresholdOperation": "opencv.threshold",
    "edu.wpi.grip.core.operations.composite.ThresholdMoving": "opencv.adaptiveThreshold",
    "edu.wpi.grip.core.operations.composite.SobelOperation": "opencv.sobel",
    "edu.wpi.grip.core.operations.composite.LaplacianOperation": "opencv.laplacian",
    "edu.wpi.grip.core.operations.composite.ErodeOperation": "opencv.erode",
    "edu.wpi.grip.core.operations.composite.DilateOperation": "opencv.dilate",
    "edu.wpi.grip.core.operations.composite.FlipOperation": "opencv.flip",
    "edu.wpi.grip.core.operations.composite.TransposeOperation": "opencv.transpose",
    # CVOperations raw ops
    "edu.wpi.grip.core.operations.CVOperations.addOperation": "opencv.add",
    "edu.wpi.grip.core.operations.CVOperations.subtractOperation": "opencv.subtract",
    "edu.wpi.grip.core.operations.CVOperations.bitwiseAndOperation": "opencv.bitwiseAnd",
    "edu.wpi.grip.core.operations.CVOperations.bitwiseOrOperation": "opencv.bitwiseOr",
    "edu.wpi.grip.core.operations.CVOperations.bitwiseXorOperation": "opencv.bitwiseXor",
    "edu.wpi.grip.core.operations.CVOperations.bitwiseNotOperation": "opencv.bitwiseNot",
}


def save_newgrip(path: str | Path, pipeline: PipelineDocumentV1) -> None:
    target = Path(path)
    target.write_text(pipeline.model_dump_json(indent=2, by_alias=True), encoding="utf-8")


def load_newgrip(path: str | Path) -> PipelineDocumentV1:
    target = Path(path)
    return PipelineDocumentV1.model_validate(json.loads(target.read_text(encoding="utf-8")))


def import_grip_xml(xml_content: str) -> tuple[PipelineDocumentV1, list[str]]:
    normalized_xml = re.sub(r"<(/?)([A-Za-z_][\w\-]*):", r"<\1", xml_content)
    root = ET.fromstring(normalized_xml)
    warnings: list[str] = []

    nodes: list[PipelineNode] = []
    edges: list[PipelineEdge] = []
    steps = root.findall(".//step")
    if not steps:
        warnings.append("No explicit <step> elements found, generated empty pipeline.")

    for idx, step in enumerate(steps):
        node_id = step.attrib.get("id", f"step-{idx+1}")
        op = step.attrib.get("operation", "opencv.noop")
        if op.startswith("edu.wpi"):
            mapped = GRIP_OP_MAP.get(op)
            if mapped:
                warnings.append(f"Mapped legacy operation {op} to {mapped}")
                op = mapped
            else:
                warnings.append(f"Unmapped legacy operation {op}, using opencv.noop")
                op = "opencv.noop"
        nodes.append(
            PipelineNode(
                id=node_id,
                op=op,
                inputs=[SocketSpec(name="in", type="image")],
                outputs=[SocketSpec(name="out", type="image")],
            )
        )

    for idx in range(max(0, len(nodes) - 1)):
        edges.append(
            PipelineEdge(
                id=f"e{idx+1}",
                **{
                    "from": {"nodeId": nodes[idx].id, "socket": "out"},
                    "to": {"nodeId": nodes[idx + 1].id, "socket": "in"},
                },
            )
        )

    if nodes and not any(n.op.startswith("source.") for n in nodes):
        source = PipelineNode(
            id="source-0",
            op="source.image",
            inputs=[],
            outputs=[SocketSpec(name="out", type="image")],
        )
        nodes.insert(0, source)
        if len(nodes) > 1:
            edges.insert(
                0,
                PipelineEdge(
                    id="source-link",
                    **{
                        "from": {"nodeId": "source-0", "socket": "out"},
                        "to": {"nodeId": nodes[1].id, "socket": "in"},
                    },
                ),
            )

    return PipelineDocumentV1(version=1, nodes=nodes, edges=edges), warnings
