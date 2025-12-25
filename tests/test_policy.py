"""
Tests for policy enforcement.
"""
from gate.policy import enforce_confidence_threshold


class TestConfidenceThreshold:
    """Tests for confidence threshold enforcement."""
    
    def test_passes_high_confidence(self):
        """Test that high confidence passes threshold."""
        passed, reason = enforce_confidence_threshold(0.85, 0.6)
        assert passed is True
        assert reason is None
    
    def test_fails_low_confidence(self):
        """Test that low confidence fails threshold."""
        passed, reason = enforce_confidence_threshold(0.42, 0.6)
        assert passed is False
        assert "below" in reason.lower()
        assert "0.42" in reason
        assert "0.60" in reason
    
    def test_exact_threshold(self):
        """Test behavior at exact threshold."""
        passed, reason = enforce_confidence_threshold(0.6, 0.6)
        assert passed is True
        assert reason is None
    
    def test_just_below_threshold(self):
        """Test just below threshold."""
        passed, reason = enforce_confidence_threshold(0.59, 0.6)
        assert passed is False
        assert reason is not None
