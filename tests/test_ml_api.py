
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_ml_prediction(monkeypatch):
    def fake_predict(code):
        return {
            "prediction": 1,
            "label": "risky",
            "risk_probability": 0.85,
            "model": "tfidf_v3"
        }

    monkeypatch.setattr(
        "backend.main.predict",
        fake_predict
    )

    response = client.post(
        "/analysis/ml",
        json={"code": "result = eval(user_input)"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["prediction"] == 1
    assert data["label"] == "risky"
    assert data["risk_probability"] == 0.85
    assert data["model"] == "tfidf_v3"


def test_ml_rejects_empty_code():
    response = client.post(
        "/analysis/ml",
        json={"code": ""}
    )

    assert response.status_code == 422


def test_ml_rejects_missing_code():
    response = client.post(
        "/analysis/ml",
        json={}
    )

    assert response.status_code == 422


def test_ml_rejects_invalid_syntax():
    response = client.post(
        "/analysis/ml",
        json={"code": "def hello("}
    )

    assert response.status_code == 422
    assert "Invalid python syntax at" in (
        response.json()["detail"]
    )


def test_ml_model_unavailable(monkeypatch):
    def fake_predict(code):
        raise FileNotFoundError(
            "Model file missing"
        )

    monkeypatch.setattr(
        "backend.main.predict",
        fake_predict
    )

    response = client.post(
        "/analysis/ml",
        json={"code": "x = 1"}
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "ML model is not available"
    )
