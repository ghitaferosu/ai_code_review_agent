from pydantic import BaseModel

from backend.models.analysis_models import AnalysisResponse,AnalyzeCodeRequest
from backend.models.ml_models import MLAnalysisResponse

class HybridAnalysisRequest(AnalyzeCodeRequest):
    pass

class HybridAnalysisResponse(BaseModel):
    static_analysis: AnalysisResponse
    ml_analysis: MLAnalysisResponse
    agreement: bool
    summary: str