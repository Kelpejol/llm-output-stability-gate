"""
Main FastAPI application for LLM output stability gate.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from gate.models import EvaluationRequest, EvaluationResponse
from gate.evaluator import evaluate_prompt
from gate.policy import enforce_confidence_threshold

app = FastAPI(
    title="LLM Output Stability Gate",
    description="Pre-execution reliability gate using UQLM",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LLM Output Stability Gate",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "llm-stability-gate"
    }


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(req: EvaluationRequest):
    """
    Evaluate prompt output stability and confidence.
    
    Args:
        req: Evaluation request with prompt and parameters
        
    Returns:
        EvaluationResponse with confidence score and pass/fail status
        
    Raises:
        HTTPException: If evaluation fails
    """
    try:
        # Evaluate prompt using UQLM
        confidence = await evaluate_prompt(
            req.prompt,
            req.num_samples,
        )

        # Enforce confidence threshold policy
        passed, reason = enforce_confidence_threshold(
            confidence,
            req.min_confidence,
        )

        return EvaluationResponse(
            confidence_score=confidence,
            passed=passed,
            reason=reason,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )
