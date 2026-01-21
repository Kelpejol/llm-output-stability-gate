"""
Rich terminal output formatting for uqlm-guard.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich import box
from typing import List, Dict, Any


console = Console()


class OutputFormatter:
    """Formats analysis results for terminal display."""
    
    @staticmethod
    def print_header(prompt: str):
        """Print analysis header."""
        console.print()
        console.print(Panel(
            f"[bold cyan]Analyzing Prompt[/bold cyan]\n{prompt}",
            border_style="cyan",
            box=box.ROUNDED
        ))
        console.print()
    
    @staticmethod
    def print_analyzing(num_samples: int, model: str):
        """Show analyzing progress."""
        console.print(f"[yellow]⚡ Generating {num_samples} responses using {model}...[/yellow]")
    
    @staticmethod
    def print_confidence_score(score: float, recommendation: str):
        """Print confidence score with color coding."""
        console.print()
        
        # Determine color and emoji
        if score >= 0.8:
            color = "green"
            emoji = "✅"
            level = "HIGH CONFIDENCE"
        elif score >= 0.6:
            color = "yellow"
            emoji = "⚠️"
            level = "MEDIUM CONFIDENCE"
        elif score >= 0.4:
            color = "orange1"
            emoji = "⚠️"
            level = "LOW CONFIDENCE"
        else:
            color = "red"
            emoji = "🔴"
            level = "VERY LOW CONFIDENCE"
        
        # Create confidence panel
        confidence_text = f"""[bold {color}]{emoji} {level}[/bold {color}]
        
Confidence Score: [{color}]{score:.2f}/1.0[/{color}]

[italic]{recommendation}[/italic]"""
        
        console.print(Panel(
            confidence_text,
            border_style=color,
            box=box.DOUBLE
        ))
        console.print()
    
    @staticmethod
    def print_inconsistencies(inconsistencies: List[Dict[str, Any]]):
        """Print detected inconsistencies."""
        if not inconsistencies:
            console.print("[green]✓ No major inconsistencies detected[/green]\n")
            return
        
        console.print("[bold red]⚠️  Detected Inconsistencies:[/bold red]\n")
        
        for i, inc in enumerate(inconsistencies, 1):
            severity = inc.get("severity", "unknown")
            severity_color = {
                "low": "blue",
                "medium": "yellow",
                "high": "red",
                "critical": "red bold"
            }.get(severity, "white")
            
            inc_type = inc.get("type", "unknown")
            description = inc.get("description", "No description")
            
            panel_content = f"""[{severity_color}]Severity: {severity.upper()}[/{severity_color}]
Type: {inc_type}

{description}"""
            
            console.print(Panel(
                panel_content,
                title=f"[bold]Issue #{i}[/bold]",
                border_style=severity_color,
                box=box.ROUNDED
            ))
            console.print()
    
    @staticmethod
    def print_consensus(consensus_parts: List[str]):
        """Print consensus parts."""
        if not consensus_parts:
            console.print("[yellow]⚠️  No clear consensus found across responses[/yellow]\n")
            return
        
        console.print("[bold green]✓ Consensus Elements (present in all responses):[/bold green]\n")
        
        for part in consensus_parts[:5]:  # Show first 5
            if part.strip():
                console.print(f"  • {part.strip()}")
        
        if len(consensus_parts) > 5:
            console.print(f"  [dim]... and {len(consensus_parts) - 5} more[/dim]")
        
        console.print()
    
    @staticmethod
    def print_divergence(divergences: List[Dict[str, Any]]):
        """Print divergence information."""
        if not divergences:
            return
        
        console.print("[bold]Response Divergence Analysis:[/bold]\n")
        
        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Response Pair", style="cyan")
        table.add_column("Similarity", justify="right")
        table.add_column("Diff Lines", justify="right")
        
        for div in divergences[:10]:  # Show top 10
            pair = div.get("response_pair", (0, 0))
            similarity = div.get("similarity", 0)
            diff_lines = div.get("diff_lines", 0)
            
            similarity_color = "green" if similarity > 0.8 else "yellow" if similarity > 0.5 else "red"
            
            table.add_row(
                f"#{pair[0]} vs #{pair[1]}",
                f"[{similarity_color}]{similarity:.2%}[/{similarity_color}]",
                str(diff_lines)
            )
        
        console.print(table)
        console.print()
    
    @staticmethod
    def print_responses(responses: List[str], show_full: bool = False):
        """Print generated responses."""
        console.print("[bold]Generated Responses:[/bold]\n")
        
        for i, response in enumerate(responses, 1):
            if show_full:
                console.print(Panel(
                    response,
                    title=f"[bold]Response #{i}[/bold]",
                    border_style="blue",
                    box=box.ROUNDED
                ))
            else:
                # Show preview
                preview = response[:200] + "..." if len(response) > 200 else response
                console.print(f"[cyan]Response #{i}:[/cyan]")
                console.print(f"[dim]{preview}[/dim]\n")
    
    @staticmethod
    def print_summary_stats(analysis):
        """Print summary statistics."""
        console.print("[bold]Analysis Summary:[/bold]\n")
        
        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column("Metric", style="cyan")
        table.add_column("Value")
        
        table.add_row("Model Used", analysis.model_used)
        table.add_row("Samples Generated", str(analysis.num_samples))
        table.add_row("Confidence Score", f"{analysis.confidence_score:.3f}")
        table.add_row("Inconsistencies Found", str(len(analysis.inconsistencies)))
        table.add_row("Consensus Elements", str(len(analysis.consensus_parts)))
        
        console.print(table)
        console.print()
    
    @staticmethod
    def print_benchmark_results(results: Dict[str, Any]):
        """Print benchmark results."""
        console.print()
        console.print(Panel(
            "[bold cyan]Benchmark Results[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Tests", justify="right")
        table.add_column("Avg Confidence", justify="right")
        table.add_column("High (>0.8)", justify="right", style="green")
        table.add_column("Medium (0.6-0.8)", justify="right", style="yellow")
        table.add_column("Low (<0.6)", justify="right", style="red")
        
        for category, data in results.items():
            table.add_row(
                category,
                str(data["total"]),
                f"{data['avg_confidence']:.2f}",
                str(data["high"]),
                str(data["medium"]),
                str(data["low"])
            )
        
        console.print(table)
        console.print()
    
    @staticmethod
    def print_error(message: str):
        """Print error message."""
        console.print(f"\n[bold red]❌ Error:[/bold red] {message}\n")
    
    @staticmethod
    def print_success(message: str):
        """Print success message."""
        console.print(f"\n[bold green]✓[/bold green] {message}\n")