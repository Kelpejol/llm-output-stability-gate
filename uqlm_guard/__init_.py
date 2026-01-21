"""
UQLM-Guard: AI Code Uncertainty Detection

A CLI tool that detects when AI-generated code is unreliable
by measuring output consistency using UQLM.
"""

__version__ = "1.0.0"
__author__ = "Kelpejol"
__license__ = "MIT"

from uqlm_guard.core.analyzer import UQLMAnalyzer, CodeAnalysis
from uqlm_guard.core.models import (
    Inconsistency,
    Divergence,
    AnalysisResult,
    BenchmarkResult,
    ComparisonResult,
)

__all__ = [
    "UQLMAnalyzer",
    "CodeAnalysis",
    "Inconsistency",
    "Divergence",
    "AnalysisResult",
    "BenchmarkResult",
    "ComparisonResult",
]