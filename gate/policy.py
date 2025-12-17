def enforce_confidence_threshold(score: float, threshold: float):
    if score < threshold:
        return False, (
            f"Output confidence {score:.2f} is below "
            f"required threshold {threshold:.2f}"
        )
    return True, None
