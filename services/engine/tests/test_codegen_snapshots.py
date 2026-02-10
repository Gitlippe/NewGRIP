import ast

from newgrip_engine.codegen import generate_code
from newgrip_engine.models import PipelineDocumentV1


def _pipeline() -> PipelineDocumentV1:
    return PipelineDocumentV1.model_validate(
        {
            "version": 1,
            "nodes": [
                {"id": "source-1", "op": "source.image", "inputs": [], "outputs": [{"name": "out", "type": "image"}]}
            ],
            "edges": [],
        }
    )


def _blur_pipeline() -> PipelineDocumentV1:
    return PipelineDocumentV1.model_validate(
        {
            "version": 1,
            "nodes": [
                {"id": "source-1", "op": "source.image", "inputs": [], "outputs": [{"name": "out", "type": "image"}]},
                {
                    "id": "blur-1",
                    "op": "opencv.gaussianBlur",
                    "inputs": [{"name": "in", "type": "image"}],
                    "outputs": [{"name": "out", "type": "image"}],
                    "params": [{"name": "kernel", "view": "slider", "value": 7}],
                },
            ],
            "edges": [{"id": "e1", "from": {"nodeId": "source-1", "socket": "out"}, "to": {"nodeId": "blur-1", "socket": "in"}}],
        }
    )


def _multi_step_pipeline() -> PipelineDocumentV1:
    """source -> blur -> canny pipeline."""
    return PipelineDocumentV1.model_validate(
        {
            "version": 1,
            "nodes": [
                {"id": "source-1", "op": "source.image", "inputs": [], "outputs": [{"name": "out", "type": "image"}]},
                {
                    "id": "blur-1",
                    "op": "opencv.gaussianBlur",
                    "inputs": [{"name": "in", "type": "image"}],
                    "outputs": [{"name": "out", "type": "image"}],
                    "params": [{"name": "kernel", "view": "slider", "value": 5}],
                },
                {
                    "id": "canny-1",
                    "op": "opencv.canny",
                    "inputs": [{"name": "in", "type": "image"}],
                    "outputs": [{"name": "out", "type": "image"}],
                    "params": [
                        {"name": "low", "view": "slider", "value": 50},
                        {"name": "high", "view": "slider", "value": 150},
                    ],
                },
            ],
            "edges": [
                {"id": "e1", "from": {"nodeId": "source-1", "socket": "out"}, "to": {"nodeId": "blur-1", "socket": "in"}},
                {"id": "e2", "from": {"nodeId": "blur-1", "socket": "out"}, "to": {"nodeId": "canny-1", "socket": "in"}},
            ],
        }
    )


def _erode_pipeline() -> PipelineDocumentV1:
    """Pipeline that needs numpy import (erode uses np.ones)."""
    return PipelineDocumentV1.model_validate(
        {
            "version": 1,
            "nodes": [
                {"id": "source-1", "op": "source.image", "inputs": [], "outputs": [{"name": "out", "type": "image"}]},
                {
                    "id": "erode-1",
                    "op": "opencv.erode",
                    "inputs": [{"name": "in", "type": "image"}],
                    "outputs": [{"name": "out", "type": "image"}],
                    "params": [{"name": "iterations", "view": "slider", "value": 2}],
                },
            ],
            "edges": [
                {"id": "e1", "from": {"nodeId": "source-1", "socket": "out"}, "to": {"nodeId": "erode-1", "socket": "in"}},
            ],
        }
    )


def test_python_codegen_snapshot() -> None:
    _, content = generate_code(_pipeline(), "python", "Pipe")
    assert "class Pipe" in content
    assert "import cv2" in content


def test_java_codegen_snapshot() -> None:
    _, content = generate_code(_pipeline(), "java", "Pipe")
    assert "public class Pipe" in content


def test_cpp_codegen_snapshot() -> None:
    _, content = generate_code(_pipeline(), "cpp", "Pipe")
    assert "cv::Mat run" in content


def test_python_blur_generates_real_cv2() -> None:
    _, content = generate_code(_blur_pipeline(), "python", "Pipe")
    assert "cv2.GaussianBlur" in content
    assert "(7, 7)" in content
    assert "class Pipe" in content
    assert "import cv2" in content


def test_java_blur_generates_real_imgproc() -> None:
    _, content = generate_code(_blur_pipeline(), "java", "Pipe")
    assert "Imgproc.GaussianBlur" in content
    assert "new Size(7, 7)" in content


def test_cpp_blur_generates_real_cv() -> None:
    _, content = generate_code(_blur_pipeline(), "cpp", "Pipe")
    assert "cv::GaussianBlur" in content
    assert "cv::Size(7, 7)" in content


def test_multi_step_python() -> None:
    _, content = generate_code(_multi_step_pipeline(), "python", "Pipe")
    assert "cv2.GaussianBlur" in content
    assert "cv2.Canny" in content
    assert "cv2.cvtColor" in content
    assert "import cv2" in content


def test_multi_step_java() -> None:
    _, content = generate_code(_multi_step_pipeline(), "java", "Pipe")
    assert "Imgproc.GaussianBlur" in content
    assert "Imgproc.Canny" in content


def test_multi_step_cpp() -> None:
    _, content = generate_code(_multi_step_pipeline(), "cpp", "Pipe")
    assert "cv::GaussianBlur" in content
    assert "cv::Canny" in content


def test_python_codegen_parseable() -> None:
    """Generated Python code must be valid syntax."""
    _, content = generate_code(_blur_pipeline(), "python", "Pipe")
    ast.parse(content)


def test_multi_step_python_parseable() -> None:
    """Multi-step pipeline generates valid Python syntax."""
    _, content = generate_code(_multi_step_pipeline(), "python", "Pipe")
    ast.parse(content)


def test_python_numpy_import_when_needed() -> None:
    """Erode uses np.ones, so numpy must be imported."""
    _, content = generate_code(_erode_pipeline(), "python", "Pipe")
    assert "import numpy as np" in content
    assert "cv2.erode" in content
    assert "np.ones" in content
    ast.parse(content)


def test_python_no_numpy_when_unneeded() -> None:
    """Blur does not need numpy."""
    _, content = generate_code(_blur_pipeline(), "python", "Pipe")
    assert "import numpy" not in content


def test_unknown_op_fallback() -> None:
    """Unknown operations should produce a comment, not crash."""
    pipeline = PipelineDocumentV1.model_validate(
        {
            "version": 1,
            "nodes": [
                {"id": "source-1", "op": "source.image", "inputs": [], "outputs": [{"name": "out", "type": "image"}]},
                {
                    "id": "custom-1",
                    "op": "custom.foobar",
                    "inputs": [{"name": "in", "type": "image"}],
                    "outputs": [{"name": "out", "type": "image"}],
                },
            ],
            "edges": [
                {"id": "e1", "from": {"nodeId": "source-1", "socket": "out"}, "to": {"nodeId": "custom-1", "socket": "in"}},
            ],
        }
    )
    _, py = generate_code(pipeline, "python", "Pipe")
    assert "unsupported" in py.lower()
    assert "class Pipe" in py
    ast.parse(py)

    _, java = generate_code(pipeline, "java", "Pipe")
    assert "unsupported" in java.lower()

    _, cpp = generate_code(pipeline, "cpp", "Pipe")
    assert "unsupported" in cpp.lower()


def test_source_only_python_parseable() -> None:
    """Source-only pipeline is valid Python (no code besides boilerplate)."""
    _, content = generate_code(_pipeline(), "python", "Pipe")
    ast.parse(content)
