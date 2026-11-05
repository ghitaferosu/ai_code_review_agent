from typing import Literal
from pydantic import BaseModel, Field

class MLAnalysisRequest(BaseModel):
    code:str=Field(min_length=1,max_length=100_000)


class MLAnalysisResponse(BaseModel):
    prediction:Literal[0,1]
    label:Literal["risky","not_risky"]
    risk_probability:float=Field(ge=0,le=1)
    model:str

