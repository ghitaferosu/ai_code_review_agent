
from backend.services.risk_scoring_service import calculate_risk


def test_high_risk():
    issues = [
        {"severity": "high"},
        {"severity": "high"}
    ]
    ml_result = {"prediction": 1}

    result = calculate_risk(issues, ml_result)

    assert result["static_score"] == 60
    assert result["ml_score"] == 20
    assert result["score"] == 80
    assert result["priority"] == "critical"


def test_safe_code():
    result = calculate_risk([], {"prediction": 0})

    assert result["score"] == 0
    assert result["priority"] == "low"


def test_ml_only_risk():
    result = calculate_risk([], {"prediction": 1})

    assert result["score"] == 20
    assert result["priority"] == "medium"


def test_score_capped_at_100():
    issues = [{"severity": "critical"} for _ in range(5)]

    result = calculate_risk(issues, {"prediction": 1})

    assert result["static_score"] == 80
    assert result["score"] == 100
    assert result["priority"] == "critical"
