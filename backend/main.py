from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from backend.models.analysis_models import (
AnalyzeCodeRequest, AnalysisResponse
)
from backend.services.static_analyzer import analyze_python_code

from backend.services.github_service import get_pull_request_files
from backend.services.pr_review_service import review_pull_request
import ast
from backend.models.ml_models import MLAnalysisRequest,MLAnalysisResponse
from backend.services.ml_service import predict
from backend.models.hybrid_models import HybridAnalysisRequest,HybridAnalysisResponse
from backend.services.hybrid_review_service import analyze_hybrid_code
from backend.services.hybrid_pr_review_service import review_pull_request_hybrid

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
    except httpx.HTTPStatusError as e:
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


@app.post("/analysis/ml",response_model=MLAnalysisResponse)
def analyze_ml(request: MLAnalysisRequest):
    try:
        ast.parse(request.code)
    except SyntaxError as e:
        raise HTTPException(status_code=422, detail=f"Invalid python syntax at line {e.lineno}")
    try:
        return predict(request.code)
    except OSError:
        raise HTTPException(status_code=503, detail="ML model is not available")

@app.post("/analysis/hybrid",response_model=HybridAnalysisResponse)
def analyze_hybrid(request: HybridAnalysisRequest):
    try:
        ast.parse(request.code)
    except SyntaxError as e:
        raise HTTPException(status_code=422, detail=f"Invalid python syntax at line {e.lineno}")

    try:
        return analyze_hybrid_code(request.code)
    except OSError:
        raise HTTPException(status_code=503, detail="Hybrid model is not available")


@app.post("/reviews/hybrid")
async def create_hybrid_pr_review(request:ReviewRequest):
    parts=request.repository.split("/")
    if len(parts) != 2 or not all(parts) or request.pull_request_number<1:
        raise HTTPException(status_code=400, detail="Expected owner/repository and positive PR number")
    owner, repo = parts

    try:
        return await review_pull_request_hybrid(owner, repo, request.pull_request_number)
    except httpx.HTTPStatusError as e:
        status=e.response.status_code
        raise HTTPException(status_code=status if status in (403,404,429) else 502,detail="GitHub API request failed")
    except httpx.RequestError:
        raise HTTPException(status_code=502,detail="Could not connect to GitHub API")
    except (ValueError, UnicodeDecodeError) as e:
        raise HTTPException(status_code=422,detail=str(e))
    except OSError:
        raise HTTPException(status_code=503,detail="Hybrid model is not available")