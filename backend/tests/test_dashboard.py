# Purpose: Dashboard aggregation regression tests (P08.01, T08.01–T08.05).
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_dashboard_values_trace_to_stored_evidence():
    data = client.get("/api/dashboard").json()
    # T08.01/T08.05: every metric has scope; activity entries carry routable refs.
    assert "scope" in data["open_review_findings"]
    assert isinstance(data["open_review_findings"]["value"], int)
    assert "scope" in data["recorded_incidents"]
    req = data["required_checks"]
    assert req["required"] == 5  # T08.04: full required denominator, never trimmed
    assert 0 <= req["passed"] <= req["required"]
    assert "scope" in data["validation_duration_ms"]
    assert len(data["activity"]) <= 25
    for event in data["activity"]:
        assert event["ref"]  # missing records recover via explicit ref lookup
        assert event["kind"] in ("scan", "validation", "incident", "selection")
    # T08.02: partial history yields integers + scopes, never invented series.
    assert "sparkline" not in data and "trend" not in data
