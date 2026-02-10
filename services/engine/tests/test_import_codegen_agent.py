from newgrip_engine.agent import generate_pipeline
from newgrip_engine.codegen import generate_code
from newgrip_engine.models import GenerateRequest, PipelineDocumentV1
from newgrip_engine.persistence import import_grip_xml


def test_import_grip_xml() -> None:
    xml = """
    <grip:Pipeline>
      <steps>
        <step id="s1" operation="opencv.noop" />
      </steps>
    </grip:Pipeline>
    """
    pipeline, warnings = import_grip_xml(xml)
    assert pipeline.version == 1
    assert len(pipeline.nodes) >= 1
    assert isinstance(warnings, list)


def test_import_grip_xml_maps_known_operations() -> None:
    xml = """
    <grip:Pipeline>
      <steps>
        <step id="s1" operation="edu.wpi.grip.core.operations.composite.BlurOperation" />
        <step id="s2" operation="edu.wpi.grip.core.operations.composite.CannyEdgeOperation" />
        <step id="s3" operation="edu.wpi.grip.core.operations.composite.FindContoursOperation" />
      </steps>
    </grip:Pipeline>
    """
    pipeline, warnings = import_grip_xml(xml)
    # Should have source + 3 mapped nodes
    ops = [n.op for n in pipeline.nodes]
    assert "opencv.gaussianBlur" in ops
    assert "opencv.canny" in ops
    assert "opencv.findContours" in ops
    assert "opencv.noop" not in ops


def test_import_grip_xml_unknown_falls_back() -> None:
    xml = """
    <grip:Pipeline>
      <steps>
        <step id="s1" operation="edu.wpi.grip.core.operations.composite.UnknownFutureOp" />
      </steps>
    </grip:Pipeline>
    """
    pipeline, warnings = import_grip_xml(xml)
    ops = [n.op for n in pipeline.nodes]
    assert "opencv.noop" in ops
    assert any("Unmapped" in w for w in warnings)


def test_codegen_outputs() -> None:
    pipeline = PipelineDocumentV1.model_validate(
        {
            "version": 1,
            "nodes": [{"id": "source-1", "op": "source.image", "inputs": [], "outputs": [{"name": "out", "type": "image"}]}],
            "edges": [],
        }
    )
    filename, content = generate_code(pipeline, "python", "Pipe")
    assert filename == "Pipe.py"
    assert "class Pipe" in content
    j_filename, j_content = generate_code(pipeline, "java", "Pipe")
    c_filename, c_content = generate_code(pipeline, "cpp", "Pipe")
    assert j_filename.endswith(".java")
    assert c_filename.endswith(".cpp")
    assert "class Pipe" in j_content
    assert "#include <opencv2/opencv.hpp>" in c_content


def test_agent_disabled_mode() -> None:
    result = generate_pipeline(GenerateRequest(mode="disabled", requirements="threshold"))
    assert result.pipeline.version == 1
    assert result.warnings


def test_agent_remote_mode_warning() -> None:
    result = generate_pipeline(GenerateRequest(mode="remote_model", requirements="threshold"))
    assert result.pipeline.version == 1
    assert any("Remote provider selected" in warning for warning in result.warnings)
