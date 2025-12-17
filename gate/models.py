from pydantic import BaseModel

class EvaluationRequest(BaseModel):
    prompt: str
    min_confidence: float = 0.6
    num_samples: int = 5


class EvaluationResponse(BaseModel):
    confidence_score: float
    passed: bool
    reason: str | None = None
