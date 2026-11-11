
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def fake_ml_prediction(code):
    return {
        "prediction": 1,
        "label": "risky",
        "risk_probability": 0.75,
        "model": "tfidf_v3",
    }


def test_hybrid_detects_eval(monkeypatch):
    monkeypatch.setattr(
        "backend.services.hybrid_review_service.predict",
        fake_ml_prediction,
    )

    response = client.post(
        "/analysis/hybrid",
        json={"code": "result = eval(user_input)"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["static_analysis"]["issues_count"] == 1
    assert data["ml_analysis"]["prediction"] == 1
    assert data["agreement"] is True


def test_hybrid_disagreement(monkeypatch):
    monkeypatch.setattr(
        "backend.services.hybrid_review_service.predict",
        fake_ml_prediction,
    )

    response = client.post(
        "/analysis/hybrid",
        json={"code": "x = 1"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["static_analysis"]["issues_count"] == 0
    assert data["ml_analysis"]["prediction"] == 1
    assert data["agreement"] is False


def test_hybrid_invalid_syntax():
    response = client.post(
        "/analysis/hybrid",
        json={"code": "def hello("},
    )

    assert response.status_code == 422


def test_hybrid_empty_code():
    response = client.post(
        "/analysis/hybrid",
        json={"code": ""},
    )

    assert response.status_code == 422


def test_hybrid_model_unavailable(monkeypatch):
    def unavailable(code):
        raise FileNotFoundError("Model missing")

    monkeypatch.setattr(
        "backend.services.hybrid_review_service.predict",
        unavailable,
    )

    response = client.post(
        "/analysis/hybrid",
        json={"code": "x = 1"},
    )

    assert response.status_code == 503
