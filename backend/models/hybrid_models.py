from pydantic import BaseModel,Field
from typing import Literal

from backend.models.analysis_models import AnalysisResponse,AnalyzeCodeRequest
from backend.models.ml_models import MLAnalysisResponse

class RiskScore(BaseModel):
    score: int = Field(ge=0,le=100)
    priority: Literal["low","medium","high","critical"]
    static_score: int = Field(ge=0,le=80)
    ml_score: int = Field(ge=0,le=20)

class HybridAnalysisRequest(AnalyzeCodeRequest):
    pass

class HybridAnalysisResponse(BaseModel):
    static_analysis: AnalysisResponse
    ml_analysis: MLAnalysisResponse
    agreement: bool
    summary: str
    risk: RiskScore