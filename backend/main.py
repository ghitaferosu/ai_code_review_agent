from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from backend.models.analysis_models import (
AnalyzeCodeRequest, AnalysisResponse
)
from backend.services.static_analyzer import analyze_python_code

from backend.services.github_service import get_pull_request_files
from backend.services.pr_review_service import review_pull_request

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

@app.post("/reviews/static")
async def create_static_review(request: ReviewRequest):
    try:
        parts=request.repository.split("/")
        if(
            len(parts)!=2
            or not all(parts)
            or request.pull_request_number<1
        ):
            raise HTTPException(
                status_code=400,
                detail="Expected owner/repository and positive PR number"
            )

        owner, repo = parts

        return await review_pull_request(owner, repo, request.pull_request_number)

    except httpx.HTTPStatusError as e:
        print("GitHub API ERROR", flush=True)
        print("URL:", e.request.url, flush=True)
        print("STATUS:", e.response.status_code, flush=True)
        print("MESSAGE:", e.response.text[:500], flush=True)

        raise HTTPException(
            status_code=502,
            detail="GitHub API request failed"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to GitHub API"
        )
    except (ValueError, UnicodeDecodeError) as e:
        raise HTTPException(
            status_code=502,
            detail=str(e)
        )
