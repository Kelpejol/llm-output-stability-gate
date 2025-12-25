"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator


class EvaluationRequest(BaseModel):
    """Request model for prompt evaluation."""
    
    prompt: str = Field(
        ...,
        min_length=1,
        description="The prompt to evaluate for stability"
    )
    min_confidence: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold (0.0 to 1.0)"
    )
    num_samples: int = Field(
        default=5,
        ge=2,
        le=10,
        description="Number of samples to generate for evaluation"
    )
    
    @field_validator('prompt')
    @classmethod
    def prompt_not_empty(cls, v: str) -> str:
        """Validate prompt is not just whitespace."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace only")
        return v


class EvaluationResponse(BaseModel):
    """Response model for evaluation results."""
    
    confidence_score: float = Field(
        ...,
        description="Confidence score between 0.0 and 1.0"
    )
    passed: bool = Field(
        ...,
        description="Whether the evaluation passed the threshold"
    )
    reason: str | None = Field(
        default=None,
        description="Reason for failure (if applicable)"
    )
