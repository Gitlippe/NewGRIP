from pathlib import Path

from newgrip_engine.parity import run_parity_scan


def test_parity_scan_with_fixture() -> None:
    fixtures = Path(__file__).resolve().parents[3] / "fixtures" / "grip-samples"
    results = run_parity_scan(fixtures)
    assert results
    assert results[0].source.endswith(".grip")
