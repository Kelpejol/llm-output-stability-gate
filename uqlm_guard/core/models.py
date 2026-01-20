"""
Data models for uqlm-guard.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity levels for inconsistencies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InconsistencyType(str, Enum):
    """Types of inconsistencies that can be detected."""
    STRUCTURAL = "structural"
    CONCEPTUAL = "conceptual"
    LOGICAL = "logical"
    SECURITY = "security"
    PERFORMANCE = "performance"


class Inconsistency(BaseModel):
    """Represents a detected inconsistency."""
    type: str
    severity: str
    description: str
    details: Optional[Dict[str, Any]] = None
    affected_responses: Optional[List[int]] = None


class Divergence(BaseModel):
    """Represents where responses diverge."""
    response_pair: tuple[int, int]
    diff_lines: int
    similarity: float


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    prompt: str
    confidence_score: float
    recommendation: str
    model_used: str
    num_samples: int
    responses: List[str]
    inconsistencies: List[Inconsistency]
    consensus_parts: List[str]
    divergent_parts: List[Divergence]
    
    class Config:
        json_encoders = {
            tuple: list  # Convert tuples to lists for JSON serialization
        }


class BenchmarkResult(BaseModel):
    """Result from benchmark testing."""
    category: str
    total_tests: int
    high_confidence: int
    medium_confidence: int
    low_confidence: int
    average_confidence: float
    flagged_issues: int
    
    
class ComparisonResult(BaseModel):
    """Result from comparing multiple models."""
    prompt: str
    models: Dict[str, float]  # model_name -> confidence_score
    winner: str
    confidence_spread: float