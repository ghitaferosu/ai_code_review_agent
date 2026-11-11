
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from backend.main import app

import backend.services.hybrid_pr_review_service as service


client = TestClient(app)


def fake_hybrid_analysis(code):
    risky = "eval(" in code

    issues = []

    if risky:
        issues.append({
            "line": 1,
            "category": "security",
            "severity": "high",
            "description": "Potentially unsafe eval() call",
        })

    return {
        "static_analysis": {
            "language": "python",
            "issues_count": len(issues),
            "issues": issues,
        },
        "ml_analysis": {
            "prediction": 1 if risky else 0,
            "label": "risky" if risky else "not_risky",
            "risk_probability": 0.8 if risky else 0.2,
            "model": "tfidf_v3",
        },
        "agreement": True,
        "summary": "Test analysis",
    }


def test_hybrid_pr_review(monkeypatch):
    monkeypatch.setattr(
        service,
        "get_pull_request_files",
        AsyncMock(return_value=[
            {"filename": "example.py", "status": "modified"},
            {"filename": "README.md", "status": "modified"},
        ]),
    )

    monkeypatch.setattr(
        service,
        "get_pull_request_head",
        AsyncMock(return_value="abc123"),
    )

    monkeypatch.setattr(
        service,
        "get_file_content",
        AsyncMock(return_value="result = eval(user_input)"),
    )

    monkeypatch.setattr(
        service,
        "analyze_hybrid_code",
        fake_hybrid_analysis,
    )

    response = client.post(
        "/reviews/hybrid",
        json={
            "repository": "test-owner/test-repo",
            "pull_request_number": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["repository"] == "test-owner/test-repo"
    assert data["commit_sha"] == "abc123"
    assert data["analyzed_files"] == 1
    assert data["issues_count"] == 1
    assert data["files"][0]["filename"] == "example.py"
    assert data["files"][0]["agreement"] is True


def test_hybrid_pr_without_python_files(monkeypatch):
    monkeypatch.setattr(
        service,
        "get_pull_request_files",
        AsyncMock(return_value=[
            {"filename": "README.md", "status": "modified"},
        ]),
    )

    monkeypatch.setattr(
        service,
        "get_pull_request_head",
        AsyncMock(return_value="abc123"),
    )

    response = client.post(
        "/reviews/hybrid",
        json={
            "repository": "test-owner/test-repo",
            "pull_request_number": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["analyzed_files"] == 0
    assert response.json()["issues_count"] == 0


def test_hybrid_pr_invalid_repository():
    response = client.post(
        "/reviews/hybrid",
        json={
            "repository": "invalid-name",
            "pull_request_number": 1,
        },
    )

    assert response.status_code == 400


def test_hybrid_pr_invalid_number():
    response = client.post(
        "/reviews/hybrid",
        json={
            "repository": "owner/repo",
            "pull_request_number": 0,
        },
    )

    assert response.status_code == 400


def test_hybrid_pr_too_many_files(monkeypatch):
    files = [
        {"filename": f"file_{i}.py", "status": "modified"}
        for i in range(11)
    ]

    monkeypatch.setattr(
        service,
        "get_pull_request_files",
        AsyncMock(return_value=files),
    )

    response = client.post(
        "/reviews/hybrid",
        json={
            "repository": "owner/repo",
            "pull_request_number": 1,
        },
    )

    assert response.status_code == 422
