from newgrip_engine.models import PipelineDocumentV1
from newgrip_engine.sweeps import run_parameter_sweep


def _make_threshold_pipeline() -> PipelineDocumentV1:
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
                    "op": "opencv.threshold",
                    "inputs": [{"name": "in", "type": "image"}],
                    "outputs": [{"name": "out", "type": "image"}],
                    "params": [{"name": "value", "view": "slider", "value": 80, "min": 0, "max": 255}],
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


def test_parameter_sweep() -> None:
    pipeline = _make_threshold_pipeline()
    results = run_parameter_sweep(pipeline, "step-1", "value", [50, 100, 150])
    assert len(results) == 3


def test_sweep_scores_differ() -> None:
    """Sweep with different threshold values should produce different scores."""
    pipeline = _make_threshold_pipeline()
    results = run_parameter_sweep(pipeline, "step-1", "value", [10, 80, 200])
    assert len(results) == 3
    scores = [r.score for r in results]
    # Scores should not all be identical -- different thresholds produce different outputs
    assert len(set(scores)) > 1, f"All scores are identical: {scores}"


def test_sweep_scores_are_positive() -> None:
    """Scores from real image processing should be positive."""
    pipeline = _make_threshold_pipeline()
    results = run_parameter_sweep(pipeline, "step-1", "value", [50, 150])
    for r in results:
        assert r.score > 0.0, f"Expected positive score, got {r.score}"
