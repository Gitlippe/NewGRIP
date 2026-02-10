from fastapi.testclient import TestClient

from newgrip_engine.app import app


def test_health() -> None:
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_validate_endpoint() -> None:
    client = TestClient(app)
    payload = {
        "pipeline": {
            "version": 1,
            "nodes": [
                {"id": "source-1", "op": "source.image", "inputs": [], "outputs": [{"name": "out", "type": "image"}]}
            ],
            "edges": [],
        }
    }
    res = client.post("/v1/pipelines/validate", json=payload)
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_operations_endpoint() -> None:
    client = TestClient(app)
    res = client.get("/v1/operations")
    assert res.status_code == 200
    payload = res.json()
    assert "operations" in payload
    assert len(payload["operations"]) >= 15


def test_operations_have_outputs_field() -> None:
    client = TestClient(app)
    res = client.get("/v1/operations")
    payload = res.json()
    for op in payload["operations"]:
        assert "outputs" in op
        assert isinstance(op["outputs"], list)
        assert len(op["outputs"]) >= 1
        for out in op["outputs"]:
            assert "name" in out
            assert "type" in out


def test_multi_output_operations() -> None:
    client = TestClient(app)
    res = client.get("/v1/operations")
    payload = res.json()
    multi_output_keys = {
        "find-contours", "filter-contours", "convex-hulls",
        "find-lines", "find-blobs", "distance-transform",
        "watershed", "threshold-binary",
    }
    for op in payload["operations"]:
        if op["key"] in multi_output_keys:
            assert len(op["outputs"]) == 2, f"{op['key']} should have 2 outputs"
