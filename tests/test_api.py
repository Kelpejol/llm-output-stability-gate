"""
Tests for the FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
from gate.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_returns_info(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestEvaluationEndpoint:
    """Tests for evaluation endpoint."""
    
    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_evaluate_success(self):
        """Test successful evaluation."""
        response = client.post("/evaluate", json={
            "prompt": "What is 2+2?",
            "min_confidence": 0.5,
            "num_samples": 3
        })
        assert response.status_code == 200
        data = response.json()
        assert "confidence_score" in data
        assert "passed" in data
        assert 0.0 <= data["confidence_score"] <= 1.0
    
    def test_evaluate_empty_prompt_fails(self):
        """Test that empty prompts are rejected."""
        response = client.post("/evaluate", json={
            "prompt": "",
            "min_confidence": 0.5
        })
        assert response.status_code == 422
    
    def test_evaluate_invalid_confidence(self):
        """Test invalid confidence threshold."""
        response = client.post("/evaluate", json={
            "prompt": "Test prompt",
            "min_confidence": 1.5  # Invalid: > 1.0
        })
        assert response.status_code == 422
    
    def test_evaluate_invalid_num_samples(self):
        """Test invalid number of samples."""
        response = client.post("/evaluate", json={
            "prompt": "Test prompt",
            "num_samples": 1  # Invalid: < 2
        })
        assert response.status_code == 422


class TestInputValidation:
    """Tests for input validation."""
    
    def test_missing_prompt_field(self):
        """Test request without prompt field."""
        response = client.post("/evaluate", json={
            "min_confidence": 0.5
        })
        assert response.status_code == 422
    
    def test_negative_confidence(self):
        """Test negative confidence value."""
        response = client.post("/evaluate", json={
            "prompt": "Test",
            "min_confidence": -0.5
        })
        assert response.status_code == 422
