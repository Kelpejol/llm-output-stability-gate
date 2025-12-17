from fastapi import FastAPI, HTTPException
from models import EvaluationRequest, EvaluationResponse
from evaluator import evaluate_prompt
from policy import enforce_confidence_threshold

app = FastAPI(
    title="LLM Output Stability Gate",
    description="Pre-execution reliability gate using UQLM",
)

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(req: EvaluationRequest):
    confidence = await evaluate_prompt(
        req.prompt,
        req.num_samples,
    )

    passed, reason = enforce_confidence_threshold(
        confidence,
        req.min_confidence,
    )

    if not passed:
        return EvaluationResponse(
            confidence_score=confidence,
            passed=False,
            reason=reason,
        )

    return EvaluationResponse(
        confidence_score=confidence,
        passed=True,
    )
