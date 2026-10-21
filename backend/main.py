from fastapi import FastAPI
from pydantic import BaseModel

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