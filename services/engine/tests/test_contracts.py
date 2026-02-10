from pathlib import Path


def test_openapi_contract_exists() -> None:
    path = Path(__file__).resolve().parents[1] / "openapi.yaml"
    assert path.exists()
    assert "NewGRIP Engine API" in path.read_text(encoding="utf-8")
