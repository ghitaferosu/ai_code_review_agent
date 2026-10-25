
from unittest.mock import AsyncMock, patch

import pytest

from backend.services.pr_review_service import review_pull_request


@pytest.mark.asyncio
async def test_review_detects_eval():
    files = [
        {
            "filename": "example.py",
            "status": "modified"
        }
    ]
    code = "result = eval(user_input)"
    with (
        patch(
            "backend.services.pr_review_service.get_pull_request_files",
            new_callable=AsyncMock,
            return_value=files
        ),
        patch(
            "backend.services.pr_review_service.get_pull_request_head",
            new_callable=AsyncMock,
            return_value="abc123"
        ),
        patch(
            "backend.services.pr_review_service.get_file_content",
            new_callable=AsyncMock,
            return_value=code
        )
    ):
        result = await review_pull_request(
            "test-owner", "test-repo", 1
        )

    assert result["analyzed_files"] == 1
    assert result["issues_count"] == 1
    assert result["issues"][0]["filename"] == "example.py"
    assert result["issues"][0]["line"] == 1


@pytest.mark.asyncio
async def test_review_ignores_non_python_files():
    files = [
        {
            "filename": "README.md",
            "status": "modified"
        }
    ]
    with (
        patch(
            "backend.services.pr_review_service.get_pull_request_files",
            new_callable=AsyncMock,
            return_value=files
        ),
        patch(
            "backend.services.pr_review_service.get_pull_request_head",
            new_callable=AsyncMock,
            return_value="abc123"
        )
    ):
        result = await review_pull_request(
            "test-owner", "test-repo", 1
        )

    assert result["analyzed_files"] == 0
    assert result["issues_count"] == 0
