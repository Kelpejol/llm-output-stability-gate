#!/usr/bin/env python3
"""
Benchmark runner for UQLM-Guard.

Evaluates the tool's performance across different prompt categories.
"""
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from uqlm_guard.core.analyzer import UQLMAnalyzer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich import box

console = Console()


async def run_benchmark(
    prompts_file: str = "prompts.json",
    num_samples: int = 5,
    output_file: str = None
) -> Dict[str, Any]:
    """
    Run benchmark across all prompt categories.
    
    Args:
        prompts_file: Path to prompts JSON file
        num_samples: Number of samples per prompt
        output_file: Optional output file for results
        
    Returns:
        Dictionary with benchmark results
    """
    # Load prompts
    prompts_path = Path(__file__).parent / prompts_file
    with open(prompts_path, 'r') as f:
        prompts_data = json.load(f)
    
    console.print("\n[bold cyan]🚀 UQLM-Guard Benchmark Suite[/bold cyan]\n")
    console.print(f"Loaded {sum(len(p) for p in prompts_data.values())} prompts across {len(prompts_data)} categories\n")
    
    # Initialize analyzer
    analyzer = UQLMAnalyzer()
    
    # Results storage
    results = {
        "timestamp": datetime.now().isoformat(),
        "num_samples": num_samples,
        "categories": {}
    }
    
    # Run benchmarks
    total_prompts = sum(len(p) for p in prompts_data.values())
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        overall_task = progress.add_task(
            "[cyan]Overall Progress", 
            total=total_prompts
        )
        
        for category, prompts in prompts_data.items():
            console.print(f"\n[yellow]Testing category: {category}[/yellow]")
            
            category_results = {
                "prompts": [],
                "total": len(prompts),
                "high_confidence": 0,  # >= 0.8
                "medium_confidence": 0,  # 0.6-0.8
                "low_confidence": 0,  # < 0.6
                "average_confidence": 0.0,
                "flagged_issues": 0
            }
            
            confidences = []
            
            for prompt in prompts:
                try:
                    # Analyze prompt
                    analysis = await analyzer.analyze(prompt, num_samples=num_samples)
                    
                    confidence = analysis.confidence_score
                    confidences.append(confidence)
                    
                    # Categorize confidence
                    if confidence >= 0.8:
                        category_results["high_confidence"] += 1
                    elif confidence >= 0.6:
                        category_results["medium_confidence"] += 1
                    else:
                        category_results["low_confidence"] += 1
                    
                    # Count flagged issues
                    if len(analysis.inconsistencies) > 0:
                        category_results["flagged_issues"] += 1
                    
                    # Store result
                    category_results["prompts"].append({
                        "prompt": prompt,
                        "confidence": confidence,
                        "inconsistencies": len(analysis.inconsistencies),
                        "recommendation": analysis.recommendation
                    })
                    
                    # Show progress
                    color = "green" if confidence >= 0.8 else "yellow" if confidence >= 0.6 else "red"
                    console.print(f"  [{color}]{confidence:.2f}[/{color}] - {prompt[:60]}...")
                    
                except Exception as e:
                    console.print(f"  [red]ERROR:[/red] {prompt[:60]}... - {str(e)}")
                    category_results["prompts"].append({
                        "prompt": prompt,
                        "error": str(e)
                    })
                
                progress.update(overall_task, advance=1)
            
            # Calculate average
            if confidences:
                category_results["average_confidence"] = sum(confidences) / len(confidences)
            
            results["categories"][category] = category_results
    
    # Print summary
    console.print("\n" + "="*60 + "\n")
    console.print("[bold cyan]📊 Benchmark Results Summary[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Tests", justify="right")
    table.add_column("Avg Conf.", justify="right")
    table.add_column("High", justify="right", style="green")
    table.add_column("Medium", justify="right", style="yellow")
    table.add_column("Low", justify="right", style="red")
    table.add_column("Issues", justify="right", style="orange1")
    
    for category, data in results["categories"].items():
        table.add_row(
            category,
            str(data["total"]),
            f"{data['average_confidence']:.2f}",
            str(data["high_confidence"]),
            str(data["medium_confidence"]),
            str(data["low_confidence"]),
            str(data["flagged_issues"])
        )
    
    console.print(table)
    console.print()
    
    # Overall stats
    total_tests = sum(r["total"] for r in results["categories"].values())
    total_high = sum(r["high_confidence"] for r in results["categories"].values())
    total_medium = sum(r["medium_confidence"] for r in results["categories"].values())
    total_low = sum(r["low_confidence"] for r in results["categories"].values())
    overall_avg = sum(
        r["average_confidence"] * r["total"] 
        for r in results["categories"].values()
    ) / total_tests
    
    console.print("[bold]Overall Statistics:[/bold]")
    console.print(f"  Total Tests: {total_tests}")
    console.print(f"  Average Confidence: {overall_avg:.3f}")
    console.print(f"  [green]High Confidence (≥0.8): {total_high} ({total_high/total_tests*100:.1f}%)[/green]")
    console.print(f"  [yellow]Medium Confidence (0.6-0.8): {total_medium} ({total_medium/total_tests*100:.1f}%)[/yellow]")
    console.print(f"  [red]Low Confidence (<0.6): {total_low} ({total_low/total_tests*100:.1f}%)[/red]")
    console.print()
    
    # Save results
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"benchmark_results_{timestamp}.json"
    
    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"[green]✓[/green] Results saved to: {output_path}\n")
    
    return results


async def main():
    """Main entry point."""
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not set[/red]")
        console.print("Please set it with: export OPENAI_API_KEY=your_key_here")
        return
    
    await run_benchmark()


if __name__ == "__main__":
    asyncio.run(main())