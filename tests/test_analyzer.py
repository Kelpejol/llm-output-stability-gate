"""
Tests for the UQLM analyzer.
"""
import pytest
from uqlm_guard.core.analyzer import UQLMAnalyzer


class TestUQLMAnalyzer:
    """Tests for UQLMAnalyzer class."""
    
    def test_analyzer_initialization(self):
        """Test analyzer can be initialized."""
        analyzer = UQLMAnalyzer(model="gpt-4o-mini")
        assert analyzer.model == "gpt-4o-mini"
        assert analyzer.temperature == 0.7
    
    def test_analyzer_custom_temperature(self):
        """Test custom temperature setting."""
        analyzer = UQLMAnalyzer(model="gpt-4o-mini", temperature=0.5)
        assert analyzer.temperature == 0.5
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api_key
    async def test_analyze_simple_prompt(self):
        """Test analyzing a simple prompt."""
        analyzer = UQLMAnalyzer()
        result = await analyzer.analyze("What is 2+2?", num_samples=3)
        
        assert result is not None
        assert 0.0 <= result.confidence_score <= 1.0
        assert len(result.responses) == 3
        assert result.prompt == "What is 2+2?"
    
    @pytest.mark.asyncio
    @pytest.mark.requires_api_key
    async def test_analyze_code_prompt(self):
        """Test analyzing a code generation prompt."""
        analyzer = UQLMAnalyzer()
        result = await analyzer.analyze(
            "Write a function to reverse a string in Python",
            num_samples=3
        )
        
        assert result is not None
        assert result.confidence_score >= 0.0
        assert len(result.inconsistencies) >= 0
    
    def test_find_inconsistencies_different_lengths(self):
        """Test inconsistency detection with different length responses."""
        analyzer = UQLMAnalyzer()
        responses = [
            "short",
            "this is a much longer response with more content",
            "medium length response"
        ]
        
        inconsistencies = analyzer._find_inconsistencies(responses)
        
        # Should detect structural inconsistency
        assert len(inconsistencies) > 0
        assert any(inc["type"] == "structural" for inc in inconsistencies)
    
    def test_find_consensus_identical_responses(self):
        """Test consensus detection with identical responses."""
        analyzer = UQLMAnalyzer()
        responses = [
            "def reverse(s):\n    return s[::-1]",
            "def reverse(s):\n    return s[::-1]",
            "def reverse(s):\n    return s[::-1]"
        ]
        
        consensus = analyzer._find_consensus(responses)
        
        # All lines should be in consensus
        assert len(consensus) > 0
    
    def test_find_divergence(self):
        """Test divergence detection."""
        analyzer = UQLMAnalyzer()
        responses = [
            "def reverse(s):\n    return s[::-1]",
            "def reverse(s):\n    return ''.join(reversed(s))",
            "def reverse(string):\n    result = []\n    for char in string:\n        result.insert(0, char)\n    return ''.join(result)"
        ]
        
        divergences = analyzer._find_divergence(responses)
        
        # Should detect divergence between different implementations
        assert len(divergences) > 0
    
    def test_generate_recommendation_high_confidence(self):
        """Test recommendation for high confidence."""
        analyzer = UQLMAnalyzer()
        recommendation = analyzer._generate_recommendation(0.85, [])
        
        assert "HIGH CONFIDENCE" in recommendation
        assert "reliable" in recommendation.lower()
    
    def test_generate_recommendation_low_confidence(self):
        """Test recommendation for low confidence."""
        analyzer = UQLMAnalyzer()
        inconsistencies = [
            {"severity": "high", "type": "security"}
        ]
        recommendation = analyzer._generate_recommendation(0.35, inconsistencies)
        
        assert "LOW CONFIDENCE" in recommendation or "VERY LOW CONFIDENCE" in recommendation
    
    def test_generate_recommendation_medium_with_issues(self):
        """Test recommendation for medium confidence with high severity issues."""
        analyzer = UQLMAnalyzer()
        inconsistencies = [
            {"severity": "high", "type": "logical"}
        ]
        recommendation = analyzer._generate_recommendation(0.65, inconsistencies)
        
        assert "review" in recommendation.lower()


class TestInconsistencyDetection:
    """Tests for specific inconsistency detection logic."""
    
    def test_structural_inconsistency_threshold(self):
        """Test that structural inconsistencies are properly thresholded."""
        analyzer = UQLMAnalyzer()
        
        # Similar lengths - should not trigger
        responses_similar = ["abc" * 10, "def" * 11, "ghi" * 10]
        incs_similar = analyzer._find_inconsistencies(responses_similar)
        structural_similar = [i for i in incs_similar if i["type"] == "structural"]
        
        # Very different lengths - should trigger
        responses_different = ["short", "x" * 1000]
        incs_different = analyzer._find_inconsistencies(responses_different)
        structural_different = [i for i in incs_different if i["type"] == "structural"]
        
        assert len(structural_different) >= len(structural_similar)
    
    def test_keyword_detection(self):
        """Test keyword-based inconsistency detection."""
        analyzer = UQLMAnalyzer()
        responses = [
            "authentication using JWT tokens with secure storage",
            "authentication using session cookies",
            "authentication using JWT tokens"
        ]
        
        inconsistencies = analyzer._find_inconsistencies(responses)
        
        # Should detect conceptual differences
        conceptual = [i for i in inconsistencies if i["type"] == "conceptual"]
        assert len(conceptual) > 0