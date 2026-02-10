from newgrip_engine.executor import execute_pipeline
from newgrip_engine.models import PipelineDocumentV1
from newgrip_engine.validator import validate_pipeline


def sample_pipeline() -> PipelineDocumentV1:
    return PipelineDocumentV1.model_validate(
        {
            "version": 1,
            "nodes": [
                {
                    "id": "source-1",
                    "op": "source.image",
                    "inputs": [],
                    "outputs": [{"name": "out", "type": "image"}],
                },
                {
                    "id": "step-1",
                    "op": "opencv.noop",
                    "inputs": [{"name": "in", "type": "image"}],
                    "outputs": [{"name": "out", "type": "image"}],
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "from": {"nodeId": "source-1", "socket": "out"},
                    "to": {"nodeId": "step-1", "socket": "in"},
                }
            ],
        }
    )


def test_validate_ok() -> None:
    result = validate_pipeline(sample_pipeline())
    assert result.ok


def test_execute_ok() -> None:
    result = execute_pipeline(sample_pipeline())
    assert result.ok
    assert "step-1.out" in result.outputs
