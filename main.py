#!/usr/bin/env python3
"""Credential Generator – Terminal Application.

Enter a website URL and get auto-generated fake credentials for every form
field the site asks for.

Usage:
    python main.py                  # Interactive mode
    python main.py <url>            # Direct URL mode
    python main.py <url> --locale en_IN
"""

import json
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text

from classifier import classify_fields
from generator import generate_credentials
from models import FieldType
from scraper import extract_forms, fetch_page

console = Console()

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

BANNER = r"""
[bold cyan]
  ╔═══════════════════════════════════════════════╗
  ║       🔐  Credential Generator  🔐           ║
  ║  Auto-generate fake data for any web form     ║
  ╚═══════════════════════════════════════════════╝
[/bold cyan]
"""


def show_banner():
    console.print(BANNER)


def show_fields_table(credentials: dict[str, str], title: str = "Generated Credentials"):
    """Display generated credentials in a rich table."""
    table = Table(
        title=title,
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold green",
        padding=(0, 2),
    )
    table.add_column("Field", style="bold white", min_width=20)
    table.add_column("Generated Value", style="green", min_width=30)

    for field_name, value in credentials.items():
        table.add_row(field_name, value)

    console.print()
    console.print(table)
    console.print()


def show_form_selector(forms_count: int) -> int:
    """Let the user pick a form when multiple are found."""
    console.print(
        f"\n[yellow]Found {forms_count} form(s) on this page.[/yellow]"
    )
    if forms_count == 1:
        return 0

    choices = [str(i + 1) for i in range(forms_count)]
    choice = Prompt.ask(
        f"Which form do you want to generate credentials for? [1-{forms_count}]",
        choices=choices,
        default="1",
    )
    return int(choice) - 1


# ---------------------------------------------------------------------------
# Core workflow
# ---------------------------------------------------------------------------

def process_url(url: str, locale: str = "en_US") -> dict[str, str] | None:
    """Fetch a URL, detect form fields, and generate credentials."""
    # Fetch page
    with console.status("[bold blue]Fetching page...", spinner="dots"):
        try:
            html = fetch_page(url)
        except Exception as e:
            console.print(f"[bold red]Error fetching page:[/bold red] {e}")
            return None

    # Extract forms
    with console.status("[bold blue]Analyzing form fields...", spinner="dots"):
        forms = extract_forms(html, base_url=url)

    if not forms:
        console.print(
            Panel(
                "[yellow]No forms detected on this page.[/yellow]\n"
                "This could mean:\n"
                "  • The page uses JavaScript to render forms (try installing Playwright)\n"
                "  • The URL doesn't contain a form\n"
                "  • The page requires authentication to access the form",
                title="⚠️  No Forms Found",
                border_style="yellow",
            )
        )
        return None

    # Pick form
    form_idx = show_form_selector(len(forms))
    raw_fields = forms[form_idx]

    if not raw_fields:
        console.print("[yellow]Selected form has no fillable fields.[/yellow]")
        return None

    # Show detected fields
    console.print(f"\n[cyan]Detected {len(raw_fields)} field(s):[/cyan]")

    # Classify
    classified = classify_fields(raw_fields)
    fillable = [f for f in classified if f.semantic_type != FieldType.SKIP]

    if not fillable:
        console.print("[yellow]No fillable fields found in this form.[/yellow]")
        return None

    # Show what we detected
    detection_table = Table(
        title="Detected Fields",
        show_header=True,
        header_style="bold blue",
        border_style="dim",
    )
    detection_table.add_column("Field", style="white")
    detection_table.add_column("Detected Type", style="cyan")
    detection_table.add_column("HTML Type", style="dim")

    for cf in fillable:
        detection_table.add_row(
            cf.display_name,
            cf.semantic_type.name.replace("_", " ").title(),
            cf.raw.input_type,
        )

    console.print(detection_table)

    # Generate
    credentials = generate_credentials(fillable, locale=locale)
    return credentials


# ---------------------------------------------------------------------------
# Save / Export
# ---------------------------------------------------------------------------

def save_credentials(credentials: dict[str, str], url: str):
    """Save credentials to a JSON file."""
    output_dir = Path("generated_credentials")
    output_dir.mkdir(exist_ok=True)

    # Create a safe filename from the URL
    from urllib.parse import urlparse

    parsed = urlparse(url)
    safe_name = parsed.netloc.replace(".", "_").replace(":", "_")
    if not safe_name:
        safe_name = "credentials"

    filepath = output_dir / f"{safe_name}.json"

    # If file exists, load and append
    existing: list[dict] = []
    if filepath.exists():
        with open(filepath) as f:
            existing = json.load(f)
            if isinstance(existing, dict):
                existing = [existing]

    existing.append(credentials)

    with open(filepath, "w") as f:
        json.dump(existing, f, indent=2)

    console.print(f"[green]✓ Saved to {filepath}[/green]")


def copy_to_clipboard(credentials: dict[str, str]):
    """Copy credentials to clipboard as formatted text."""
    try:
        import pyperclip

        text = "\n".join(f"{k}: {v}" for k, v in credentials.items())
        pyperclip.copy(text)
        console.print("[green]✓ Copied to clipboard![/green]")
    except ImportError:
        console.print(
            "[yellow]pyperclip not installed – "
            "install it with: pip install pyperclip[/yellow]"
        )
    except Exception as e:
        console.print(f"[yellow]Could not copy: {e}[/yellow]")


# ---------------------------------------------------------------------------
# Interactive loop
# ---------------------------------------------------------------------------

def interactive_loop():
    """Main interactive loop."""
    show_banner()

    # Check for CLI argument
    url = None
    locale = "en_US"

    args = sys.argv[1:]
    if args:
        url = args[0]
        if "--locale" in args:
            idx = args.index("--locale")
            if idx + 1 < len(args):
                locale = args[idx + 1]

    while True:
        if not url:
            url = Prompt.ask(
                "\n[bold cyan]Enter website URL[/bold cyan]",
                default="",
            ).strip()

        if not url:
            console.print("[yellow]No URL provided. Exiting.[/yellow]")
            break

        # Ensure URL has scheme
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        credentials = process_url(url, locale=locale)

        if credentials:
            show_fields_table(credentials)

            # Post-generation actions
            while True:
                action = Prompt.ask(
                    "[bold]What would you like to do?[/bold]",
                    choices=["regenerate", "save", "copy", "new", "quit"],
                    default="new",
                )

                if action == "regenerate":
                    credentials = process_url(url, locale=locale)
                    if credentials:
                        show_fields_table(credentials)
                elif action == "save":
                    save_credentials(credentials, url)
                elif action == "copy":
                    copy_to_clipboard(credentials)
                elif action == "new":
                    break
                elif action == "quit":
                    console.print("[bold cyan]Goodbye! 👋[/bold cyan]")
                    return

        url = None  # Reset for next iteration

        if not Confirm.ask("\n[bold]Try another URL?[/bold]", default=True):
            break

    console.print("[bold cyan]Goodbye! 👋[/bold cyan]")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        interactive_loop()
    except KeyboardInterrupt:
        console.print("\n[bold cyan]Interrupted. Goodbye! 👋[/bold cyan]")
        sys.exit(0)
