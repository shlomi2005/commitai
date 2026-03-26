import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from commitai import __version__
from commitai.git_ops import (
    commit,
    get_repo_context,
    get_staged_diff,
    has_staged_changes,
    is_git_repo,
)
from commitai.ai_client import generate_messages

console = Console()

PROVIDERS = ["anthropic", "openai", "ollama"]


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(__version__, "-v", "--version")
@click.option("--provider", "-p", default="anthropic", type=click.Choice(PROVIDERS), help="AI provider")
@click.option("--model", "-m", default=None, help="Model override")
@click.option("--count", "-n", default=5, help="Number of suggestions", show_default=True)
@click.option("--yes", "-y", is_flag=True, help="Auto-select the first suggestion")
def cli(ctx, provider, model, count, yes):
    """commitai — AI-powered git commit messages ✨

    Analyzes your staged changes and generates smart commit messages
    following the Conventional Commits specification.

    \b
    Providers:
      anthropic  Claude (default) — set ANTHROPIC_API_KEY
      openai     GPT models       — set OPENAI_API_KEY
      ollama     Local models     — free, no API key needed

    \b
    Examples:
      git add -p && commitai
      commitai --provider ollama
      commitai --provider openai --model gpt-4o
      commitai --count 3 --yes
    """
    if ctx.invoked_subcommand is not None:
        return

    if not is_git_repo():
        console.print("[red]❌ Not a git repository.[/red]")
        sys.exit(1)

    if not has_staged_changes():
        console.print("[yellow]⚠️  No staged changes. Run [bold]git add[/bold] first.[/yellow]")
        sys.exit(1)

    with console.status("[bold cyan]Analyzing your changes...[/bold cyan]"):
        diff = get_staged_diff()
        context = get_repo_context()

    with console.status(f"[bold cyan]Generating {count} commit messages with {provider}...[/bold cyan]"):
        try:
            messages = generate_messages(diff, context, count=count, provider=provider, model=model)
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            sys.exit(1)

    if not messages:
        console.print("[red]❌ No messages generated. Please try again.[/red]")
        sys.exit(1)

    console.print()
    console.print(Panel.fit(
        f"[bold]Branch:[/bold] [cyan]{context.get('branch', 'main')}[/cyan]",
        title="[bold green]commitai[/bold green]",
        border_style="green",
    ))
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("№", style="bold cyan", no_wrap=True)
    table.add_column("Message", style="white")

    for i, msg in enumerate(messages, 1):
        table.add_row(f"[{i}]", msg)

    console.print(table)
    console.print()

    if yes:
        chosen = messages[0]
    else:
        choices = [str(i) for i in range(1, len(messages) + 1)] + ["e", "q"]
        answer = Prompt.ask(
            "[bold]Select[/bold] (1-{n}), [bold]e[/bold]dit, or [bold]q[/bold]uit".format(n=len(messages)),
            choices=choices,
            show_choices=False,
        )

        if answer == "q":
            console.print("[dim]Aborted.[/dim]")
            sys.exit(0)
        elif answer == "e":
            chosen = click.edit(messages[0])
            if not chosen:
                console.print("[dim]Aborted.[/dim]")
                sys.exit(0)
            chosen = chosen.strip()
        else:
            chosen = messages[int(answer) - 1]

    if commit(chosen):
        console.print(f"\n[bold green]✓ Committed:[/bold green] {chosen}")
    else:
        console.print("[red]❌ Commit failed.[/red]")
        sys.exit(1)


@cli.command()
def install_hook():
    """Install commitai as a prepare-commit-msg git hook."""
    import os
    import stat

    hook_path = ".git/hooks/prepare-commit-msg"
    if not os.path.exists(".git"):
        console.print("[red]❌ Not a git repository.[/red]")
        sys.exit(1)

    hook_content = """#!/bin/sh
# commitai prepare-commit-msg hook
if [ -z "$2" ]; then
    commitai --yes 2>/dev/null && exit 1 || true
fi
"""
    with open(hook_path, "w") as f:
        f.write(hook_content)

    os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IEXEC)
    console.print(f"[green]✓ Hook installed at {hook_path}[/green]")


def main():
    cli()


if __name__ == "__main__":
    main()
