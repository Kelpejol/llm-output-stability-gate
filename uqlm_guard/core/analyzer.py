"""
Core uncertainty analysis engine using UQLM.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from uqlm import BlackBoxUQ
from langchain.chat_models import ChatOpenAI
import os
import difflib
from collections import Counter


@dataclass
class CodeAnalysis:
    """Results from uncertainty analysis."""
    prompt: str
    responses: List[str]
    confidence_score: float
    inconsistencies: List[Dict[str, Any]]
    consensus_parts: List[str]
    divergent_parts: List[Dict[str, Any]]
    recommendation: str
    model_used: str
    num_samples: int


class UQLMAnalyzer:
    """Analyzes code generation uncertainty using UQLM."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Initialize the analyzer.
        
        Args:
            model: OpenAI model to use
            temperature: Sampling temperature for diversity
        """
        self.model = model
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        # Initialize UQLM
        self.uq = BlackBoxUQ(
            llm=self.llm,
            scorers=["semantic_negentropy"],
            use_best=True,
        )
    
    async def analyze(self, prompt: str, num_samples: int = 5) -> CodeAnalysis:
        """
        Analyze uncertainty in LLM responses.
        
        Args:
            prompt: The prompt to analyze
            num_samples: Number of responses to generate
            
        Returns:
            CodeAnalysis with detailed results
        """
        # Generate multiple responses
        results = await self.uq.generate_and_score(
            prompts=[prompt],
            num_responses=num_samples,
        )
        
        # Extract data
        df = results.to_df()
        confidence = float(df["confidence_score"].iloc[0])
        responses = [df[f"response_{i}"].iloc[0] for i in range(num_samples)]
        
        # Analyze inconsistencies
        inconsistencies = self._find_inconsistencies(responses)
        consensus_parts = self._find_consensus(responses)
        divergent_parts = self._find_divergence(responses)
        recommendation = self._generate_recommendation(confidence, inconsistencies)
        
        return CodeAnalysis(
            prompt=prompt,
            responses=responses,
            confidence_score=confidence,
            inconsistencies=inconsistencies,
            consensus_parts=consensus_parts,
            divergent_parts=divergent_parts,
            recommendation=recommendation,
            model_used=self.model,
            num_samples=num_samples,
        )
    
    def _find_inconsistencies(self, responses: List[str]) -> List[Dict[str, Any]]:
        """Find major inconsistencies across responses."""
        inconsistencies = []
        
        # Check length variance (indicates structural differences)
        lengths = [len(r) for r in responses]
        avg_length = sum(lengths) / len(lengths)
        length_variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        
        if length_variance > avg_length * 0.5:  # High variance
            inconsistencies.append({
                "type": "structural",
                "severity": "high",
                "description": f"Response lengths vary significantly ({min(lengths)} to {max(lengths)} chars)",
                "details": {"lengths": lengths, "variance": length_variance}
            })
        
        # Check for keyword disagreements
        keywords_per_response = []
        for response in responses:
            # Extract potential keywords (simplified)
            words = response.lower().split()
            keywords = [w for w in words if len(w) > 5]  # Simple heuristic
            keywords_per_response.append(set(keywords))
        
        # Find words that appear in some but not all responses
        all_keywords = set().union(*keywords_per_response)
        for keyword in all_keywords:
            count = sum(1 for kw_set in keywords_per_response if keyword in kw_set)
            if 0 < count < len(responses):  # Appears in some but not all
                inconsistencies.append({
                    "type": "conceptual",
                    "severity": "medium",
                    "description": f"Keyword '{keyword}' appears in {count}/{len(responses)} responses",
                    "keyword": keyword,
                    "frequency": count / len(responses)
                })
        
        return inconsistencies
    
    def _find_consensus(self, responses: List[str]) -> List[str]:
        """Find parts where all responses agree."""
        if not responses:
            return []
        
        # Use difflib to find common sequences
        consensus = []
        
        # Split responses into lines for comparison
        lines_per_response = [r.split('\n') for r in responses]
        
        # Find lines that appear in all responses
        if lines_per_response:
            first_lines = set(lines_per_response[0])
            common_lines = first_lines.copy()
            
            for lines in lines_per_response[1:]:
                common_lines &= set(lines)
            
            consensus = list(common_lines)
        
        return consensus
    
    def _find_divergence(self, responses: List[str]) -> List[Dict[str, Any]]:
        """Find where responses diverge."""
        divergences = []
        
        # Compare each pair of responses
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                diff = difflib.unified_diff(
                    responses[i].split('\n'),
                    responses[j].split('\n'),
                    lineterm='',
                )
                
                diff_lines = list(diff)
                if len(diff_lines) > 5:  # Significant difference
                    divergences.append({
                        "response_pair": (i, j),
                        "diff_lines": len(diff_lines),
                        "similarity": difflib.SequenceMatcher(
                            None, responses[i], responses[j]
                        ).ratio()
                    })
        
        return divergences
    
    def _generate_recommendation(
        self, 
        confidence: float, 
        inconsistencies: List[Dict[str, Any]]
    ) -> str:
        """Generate a recommendation based on analysis."""
        if confidence >= 0.8:
            return "HIGH CONFIDENCE - Output appears reliable"
        elif confidence >= 0.6:
            severity_counts = Counter(inc["severity"] for inc in inconsistencies)
            if severity_counts.get("high", 0) > 0:
                return "MEDIUM CONFIDENCE - Review flagged issues before use"
            return "MEDIUM CONFIDENCE - Acceptable with review"
        elif confidence >= 0.4:
            return "LOW CONFIDENCE - Manual review required, significant uncertainty"
        else:
            return "VERY LOW CONFIDENCE - Do not use, highly unreliable output"