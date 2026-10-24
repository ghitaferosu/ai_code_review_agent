from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from backend.models.analysis_models import (
AnalyzeCodeRequest, AnalysisResponse
)
from backend.services.static_analyzer import analyze_python_code

from backend.services.github_service import get_pull_request_files

app = FastAPI(
    title="AI Code Review Agent",
    version="0.1.0"
)

class ReviewRequest(BaseModel):
    repository: str
    pull_request_number: int

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/reviews")
def create_review(request: ReviewRequest):
    return {
            "repository": request.repository,
            "pull_request_number": request.pull_request_number,
            "status":"pending",
            "message": "Review request received"
        }

@app.get("/github/{owner}/{repo}/pulls/{pull_number}/files")
async def list_pr_files(owner: str, repo: str, pull_number: int):
    try:
        files = await get_pull_request_files(owner, repo, pull_number)
        return {
            "repository": f"{owner}/{repo}",
            "pull_request_number": pull_number,
            "files_count": len(files),
            "files": files
        }
    except httpx.HTTPError as e:
        status=e.response.status_code

        raise HTTPException(
            status_code=status if status in (403,404,429) else 502,
            detail="GitHub API request failed"
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to GitHub API"
        )

@app.post("/analysis/python",response_model=AnalysisResponse)
def analyze_python(request: AnalyzeCodeRequest):
    issues=analyze_python_code(request.code)
    return AnalysisResponse(
        language="python",
        issues_count=len(issues),
        issues=issues
    )