import numpy as np

from newgrip_engine.models import PipelineNode, SocketSpec
from newgrip_engine.operations import OperationRegistry


def _node(op: str):
    return PipelineNode(
        id="n1",
        op=op,
        inputs=[SocketSpec(name="in", type="image")],
        outputs=[SocketSpec(name="out", type="image")],
    )


def test_catalog_has_expected_scale() -> None:
    catalog = OperationRegistry.catalog()
    assert len(catalog) >= 17
    categories = {c.category for c in catalog}
    assert {"Filtering", "Thresholding", "Edges", "Contours", "Morphology", "Color", "Neural"} <= categories


def test_real_op_execution_paths() -> None:
    reg = OperationRegistry()
    image = np.zeros((64, 64, 3), dtype=np.uint8)
    image[10:50, 20:44] = (200, 200, 200)

    for op in ["opencv.gaussianBlur", "opencv.threshold", "opencv.canny", "opencv.findContours", "opencv.dilate"]:
        out = reg.run(op, _node(op), {"in": image}, {})
        assert "out" in out
