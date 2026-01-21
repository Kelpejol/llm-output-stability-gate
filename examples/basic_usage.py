#!/usr/bin/env python3
"""
Basic usage examples for UQLM-Guard.
"""
import asyncio
import os
from uqlm_guard import UQLMAnalyzer


async def example_1_simple_analysis():
    """Example 1: Simple prompt analysis."""
    print("\n" + "="*60)
    print("Example 1: Simple Prompt Analysis")
    print("="*60 + "\n")
    
    analyzer = UQLMAnalyzer()
    
    prompt = "Write a function to calculate the factorial of a number"
    print(f"Prompt: {prompt}\n")
    
    analysis = await analyzer.analyze(prompt, num_samples=5)
    
    print(f"Confidence Score: {analysis.confidence_score:.3f}")
    print(f"Recommendation: {analysis.recommendation}")
    print(f"Inconsistencies Found: {len(analysis.inconsistencies)}")
    print()


async def example_2_security_code():
    """Example 2: Security-sensitive code (typically low confidence)."""
    print("\n" + "="*60)
    print("Example 2: Security-Sensitive Code")
    print("="*60 + "\n")
    
    analyzer = UQLMAnalyzer()
    
    prompt = "Implement JWT token authentication with secure storage"
    print(f"Prompt: {prompt}\n")
    
    analysis = await analyzer.analyze(prompt, num_samples=5)
    
    print(f"Confidence Score: {analysis.confidence_score:.3f}")
    print(f"Recommendation: {analysis.recommendation}\n")
    
    if analysis.inconsistencies:
        print("Detected Issues:")
        for i, issue in enumerate(analysis.inconsistencies[:3], 1):
            print(f"  {i}. [{issue['severity'].upper()}] {issue['description']}")
    print()


async def example_3_compare_prompts():
    """Example 3: Compare multiple prompts."""
    print("\n" + "="*60)
    print("Example 3: Comparing Multiple Prompts")
    print("="*60 + "\n")
    
    analyzer = UQLMAnalyzer()
    
    prompts = [
        "Write a function to reverse a string",
        "Implement a binary search tree",
        "Create a distributed rate limiter with Redis"
    ]
    
    for prompt in prompts:
        analysis = await analyzer.analyze(prompt, num_samples=3)
        status = "✅" if analysis.confidence_score >= 0.8 else "⚠️" if analysis.confidence_score >= 0.6 else "❌"
        print(f"{status} {analysis.confidence_score:.2f} - {prompt}")
    
    print()


async def example_4_detailed_analysis():
    """Example 4: Detailed analysis with response inspection."""
    print("\n" + "="*60)
    print("Example 4: Detailed Analysis")
    print("="*60 + "\n")
    
    analyzer = UQLMAnalyzer()
    
    prompt = "Implement consistent hashing for load balancing"
    print(f"Prompt: {prompt}\n")
    
    analysis = await analyzer.analyze(prompt, num_samples=5)
    
    print(f"Confidence Score: {analysis.confidence_score:.3f}")
    print(f"Model: {analysis.model_used}")
    print(f"Samples: {analysis.num_samples}\n")
    
    print("Response Analysis:")
    print(f"  - Consensus elements: {len(analysis.consensus_parts)}")
    print(f"  - Divergent pairs: {len(analysis.divergent_parts)}")
    print(f"  - Inconsistencies: {len(analysis.inconsistencies)}\n")
    
    if analysis.consensus_parts:
        print("Sample Consensus (first 3):")
        for part in analysis.consensus_parts[:3]:
            if part.strip():
                print(f"  • {part.strip()[:80]}...")
    print()


async def main():
    """Run all examples."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set")
        print("Please set it with: export OPENAI_API_KEY=your_key_here")
        return
    
    print("\n🛡️  UQLM-Guard - Usage Examples")
    
    await example_1_simple_analysis()
    await example_2_security_code()
    await example_3_compare_prompts()
    await example_4_detailed_analysis()
    
    print("="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())