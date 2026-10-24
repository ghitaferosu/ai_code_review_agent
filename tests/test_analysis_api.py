from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_analyze_eval():
    response = client.post(
        "/analysis/python",
        json={"code": "result = eval(user_input)"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["language"] == "python"
    assert data["issues_count"] == 1
    assert data["issues"][0]["category"] == "security"
    assert data["issues"][0]["line"] == 1

def test_analyze_safe_code():
    response = client.post(
        "/analysis/python",
        json={"code": "x = 10\nprint(x)"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["issues_count"] == 0
    assert data["issues"] == []

def test_empty_code():
    response = client.post(
        "/analysis/python",
        json={"code": ""}
    )

    assert response.status_code == 422
