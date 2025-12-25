"""
Policy enforcement for confidence thresholds.
"""


def enforce_confidence_threshold(score: float, threshold: float) -> tuple[bool, str | None]:
    """
    Enforce confidence threshold policy.
    
    Args:
        score: Confidence score from evaluation (0.0 to 1.0)
        threshold: Minimum required confidence
        
    Returns:
        Tuple of (passed, reason)
        - passed: True if score meets threshold
        - reason: None if passed, error message if failed
        
    Example:
        >>> enforce_confidence_threshold(0.75, 0.6)
        (True, None)
        
        >>> enforce_confidence_threshold(0.42, 0.6)
        (False, "Output confidence 0.42 is below required threshold 0.60")
    """
    if score < threshold:
        return False, (
            f"Output confidence {score:.2f} is below "
            f"required threshold {threshold:.2f}"
        )
    return True, None
