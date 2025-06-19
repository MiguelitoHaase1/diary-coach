"""
Main entry point for the Diary Coach system.

This module provides the command-line interface and application startup logic
for the multi-agent coaching system.
"""

import asyncio
import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.option('--mode', default='text', help='Interaction mode: text or voice')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(mode: str, debug: bool):
    """Start the Diary Coach multi-agent coaching system."""
    
    console.print(Panel.fit(
        "[bold blue]Diary Coach[/bold blue]\n"
        "Multi-Agent Coaching System\n"
        f"Mode: {mode.upper()}",
        title="🤖 AI Coach"
    ))
    
    if mode == 'text':
        console.print("[green]Starting text-based coaching session...[/green]")
        # TODO: Initialize text-based coaching interface
        console.print("[yellow]Implementation coming in Lesson 1![/yellow]")
    elif mode == 'voice':
        console.print("[yellow]Voice mode will be available in Phase 4[/yellow]")
    else:
        console.print(f"[red]Unknown mode: {mode}[/red]")
        return
    
    console.print("[dim]Press Ctrl+C to exit[/dim]")
    
    try:
        # Keep the application running
        asyncio.run(run_coaching_session())
    except KeyboardInterrupt:
        console.print("\n[blue]Goodbye! Remember to reflect on your day.[/blue]")


async def run_coaching_session():
    """Run the main coaching session loop."""
    # TODO: Implement coaching session logic
    await asyncio.sleep(0.1)  # Placeholder
    console.print("[dim]Coaching session logic not yet implemented[/dim]")


if __name__ == "__main__":
    main()