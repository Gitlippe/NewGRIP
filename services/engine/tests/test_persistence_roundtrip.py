from pathlib import Path

from newgrip_engine.models import PipelineDocumentV1
from newgrip_engine.persistence import load_newgrip, save_newgrip


def test_roundtrip(tmp_path: Path) -> None:
    pipeline = PipelineDocumentV1.model_validate(
        {
            "version": 1,
            "nodes": [
                {"id": "source-1", "op": "source.image", "inputs": [], "outputs": [{"name": "out", "type": "image"}]}
            ],
            "edges": [],
        }
    )
    path = tmp_path / "sample.newgrip.json"
    save_newgrip(path, pipeline)
    loaded = load_newgrip(path)
    assert loaded.version == 1
    assert loaded.nodes[0].id == "source-1"
