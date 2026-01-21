"""
CLI interface for uqlm-guard.
"""
import asyncio
import click
import json
import os
from pathlib import Path
from typing import Optional

from uqlm_guard.core.analyzer import UQLMAnalyzer
from uqlm_guard.cli.formatter import OutputFormatter, console


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🛡️  UQLM-Guard - AI Code Uncertainty Detection
    
    Detect when AI-generated code is unreliable by measuring output consistency.
    """
    pass


@cli.command()
@click.argument('prompt', type=str)
@click.option('--samples', '-n', default=5, help='Number of responses to generate (2-10)')
@click.option('--model', '-m', default='gpt-4o-mini', help='Model to use')
@click.option('--temperature', '-t', default=0.7, help='Sampling temperature')
@click.option('--show-responses', '-r', is_flag=True, help='Show full responses')
@click.option('--json-output', '-j', is_flag=True, help='Output as JSON')
@click.option('--output', '-o', type=click.Path(), help='Save results to file')
def review(
    prompt: str,
    samples: int,
    model: str,
    temperature: float,
    show_responses: bool,
    json_output: bool,
    output: Optional[str]
):
    """
    Review a prompt for output uncertainty.
    
    Example:
        uqlm-guard review "Write a binary search function in Python"
    """
    if not os.getenv("OPENAI_API_KEY"):
        OutputFormatter.print_error(
            "OPENAI_API_KEY not found in environment variables.\n"
            "Please set it with: export OPENAI_API_KEY=your_key_here"
        )
        return
    
    if samples < 2 or samples > 10:
        OutputFormatter.print_error("Number of samples must be between 2 and 10")
        return
    
    async def run_analysis():
        if not json_output:
            OutputFormatter.print_header(prompt)
            OutputFormatter.print_analyzing(samples, model)
        
        analyzer = UQLMAnalyzer(model=model, temperature=temperature)
        analysis = await analyzer.analyze(prompt, num_samples=samples)
        
        if json_output:
            result = {
                "prompt": analysis.prompt,
                "confidence_score": analysis.confidence_score,
                "recommendation": analysis.recommendation,
                "model": analysis.model_used,
                "num_samples": analysis.num_samples,
                "inconsistencies": analysis.inconsistencies,
                "consensus_parts": analysis.consensus_parts,
                "divergent_parts": analysis.divergent_parts,
            }
            
            if output:
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2)
                OutputFormatter.print_success(f"Results saved to {output}")
            else:
                print(json.dumps(result, indent=2))
        else:
            # Rich terminal output
            OutputFormatter.print_confidence_score(
                analysis.confidence_score,
                analysis.recommendation
            )
            OutputFormatter.print_inconsistencies(analysis.inconsistencies)
            OutputFormatter.print_consensus(analysis.consensus_parts)
            OutputFormatter.print_divergence(analysis.divergent_parts)
            
            if show_responses:
                OutputFormatter.print_responses(analysis.responses, show_full=True)
            
            OutputFormatter.print_summary_stats(analysis)
            
            if output:
                with open(output, 'w') as f:
                    json.dump({
                        "prompt": analysis.prompt,
                        "confidence_score": analysis.confidence_score,
                        "recommendation": analysis.recommendation,
                        "responses": analysis.responses,
                    }, f, indent=2)
                OutputFormatter.print_success(f"Results saved to {output}")
    
    asyncio.run(run_analysis())


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--samples', '-n', default=5, help='Number of responses per prompt')
@click.option('--model', '-m', default='gpt-4o-mini', help='Model to use')
def batch(file_path: str, samples: int, model: str):
    """
    Analyze multiple prompts from a file (one per line).
    
    Example:
        uqlm-guard batch prompts.txt
    """
    if not os.getenv("OPENAI_API_KEY"):
        OutputFormatter.print_error(
            "OPENAI_API_KEY not found in environment variables"
        )
        return
    
    with open(file_path, 'r') as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    if not prompts:
        OutputFormatter.print_error(f"No prompts found in {file_path}")
        return
    
    console.print(f"\n[cyan]Found {len(prompts)} prompts to analyze[/cyan]\n")
    
    async def run_batch():
        analyzer = UQLMAnalyzer(model=model)
        results = []
        
        for i, prompt in enumerate(prompts, 1):
            console.print(f"[yellow]Analyzing prompt {i}/{len(prompts)}...[/yellow]")
            analysis = await analyzer.analyze(prompt, num_samples=samples)
            
            results.append({
                "prompt": prompt,
                "confidence": analysis.confidence_score,
                "recommendation": analysis.recommendation,
            })
            
            # Show brief result
            color = "green" if analysis.confidence_score >= 0.8 else "yellow" if analysis.confidence_score >= 0.6 else "red"
            console.print(f"  [{color}]Confidence: {analysis.confidence_score:.2f}[/{color}] - {prompt[:60]}...\n")
        
        # Summary
        console.print("\n[bold]Batch Analysis Summary:[/bold]\n")
        avg_confidence = sum(r["confidence"] for r in results) / len(results)
        high_conf = sum(1 for r in results if r["confidence"] >= 0.8)
        medium_conf = sum(1 for r in results if 0.6 <= r["confidence"] < 0.8)
        low_conf = sum(1 for r in results if r["confidence"] < 0.6)
        
        console.print(f"Total Prompts: {len(results)}")
        console.print(f"Average Confidence: {avg_confidence:.2f}")
        console.print(f"[green]High Confidence (≥0.8): {high_conf}[/green]")
        console.print(f"[yellow]Medium Confidence (0.6-0.8): {medium_conf}[/yellow]")
        console.print(f"[red]Low Confidence (<0.6): {low_conf}[/red]\n")
    
    asyncio.run(run_batch())


@cli.command()
@click.argument('prompt', type=str)
@click.option('--models', '-m', multiple=True, default=['gpt-4o-mini', 'gpt-4o'], help='Models to compare')
@click.option('--samples', '-n', default=5, help='Number of samples per model')
def compare(prompt: str, models: tuple, samples: int):
    """
    Compare uncertainty across different models.
    
    Example:
        uqlm-guard compare "Implement quicksort" -m gpt-4o-mini -m gpt-4o
    """
    if not os.getenv("OPENAI_API_KEY"):
        OutputFormatter.print_error(
            "OPENAI_API_KEY not found in environment variables"
        )
        return
    
    OutputFormatter.print_header(f"Comparing Models: {', '.join(models)}")
    
    async def run_comparison():
        results = {}
        
        for model in models:
            console.print(f"\n[yellow]Testing {model}...[/yellow]")
            analyzer = UQLMAnalyzer(model=model)
            analysis = await analyzer.analyze(prompt, num_samples=samples)
            results[model] = analysis.confidence_score
            
            color = "green" if analysis.confidence_score >= 0.8 else "yellow" if analysis.confidence_score >= 0.6 else "red"
            console.print(f"  [{color}]Confidence: {analysis.confidence_score:.2f}[/{color}]")
        
        # Show comparison
        console.print("\n[bold]Comparison Results:[/bold]\n")
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        
        for i, (model, score) in enumerate(sorted_results, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            color = "green" if score >= 0.8 else "yellow" if score >= 0.6 else "red"
            console.print(f"{emoji} [{color}]{model}: {score:.3f}[/{color}]")
        
        console.print(f"\n[bold green]Winner:[/bold green] {sorted_results[0][0]} ({sorted_results[0][1]:.3f})\n")
    
    asyncio.run(run_comparison())


@cli.command()
def examples():
    """Show example prompts that demonstrate uncertainty detection."""
    console.print("\n[bold cyan]Example Prompts for Testing:[/bold cyan]\n")
    
    examples_list = [
        {
            "category": "High Uncertainty (Security)",
            "prompt": "Write JWT authentication middleware",
            "reason": "Key storage and expiration times often vary"
        },
        {
            "category": "High Uncertainty (Algorithms)",
            "prompt": "Implement consistent hashing",
            "reason": "Multiple valid approaches with trade-offs"
        },
        {
            "category": "Medium Uncertainty",
            "prompt": "Create a REST API rate limiter",
            "reason": "Implementation details may differ"
        },
        {
            "category": "Low Uncertainty",
            "prompt": "Write a function to reverse a string",
            "reason": "Simple, well-defined task"
        },
    ]
    
    for ex in examples_list:
        console.print(f"[bold yellow]{ex['category']}[/bold yellow]")
        console.print(f"  Prompt: [cyan]{ex['prompt']}[/cyan]")
        console.print(f"  Why: [dim]{ex['reason']}[/dim]\n")
    
    console.print("[dim]Try: uqlm-guard review \"Write JWT authentication middleware\"[/dim]\n")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()