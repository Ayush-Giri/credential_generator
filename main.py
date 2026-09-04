#!/usr/bin/env python3
"""Credential Generator – Terminal Application.

Usage:
    generate <url>                  # Generate credentials for a website
    generate <url> --locale en_IN   # Use a specific locale
    generate <url> --json           # Output as JSON
"""

import json
import sys

from rich.console import Console
from rich.table import Table

from classifier import classify_fields
from generator import generate_credentials
from models import FieldType
from scraper import extract_forms, fetch_page

console = Console()


def process_url(url: str, locale: str = "en_US") -> dict[str, str] | None:
    """Fetch a URL, detect form fields, and generate credentials."""
    try:
        html = fetch_page(url)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return None

    forms = extract_forms(html, base_url=url)

    if not forms:
        console.print("[yellow]No forms found on this page.[/yellow]")
        return None

    # Use the largest form (most fields = likely the main signup/registration form)
    best_form = max(forms, key=len)

    classified = classify_fields(best_form)
    fillable = [f for f in classified if f.semantic_type != FieldType.SKIP]

    if not fillable:
        console.print("[yellow]No fillable fields found.[/yellow]")
        return None

    return generate_credentials(fillable, locale=locale)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        console.print("[bold cyan]🔐 Credential Generator[/bold cyan]")
        console.print("\nUsage:  [green]generate <url>[/green]  [dim]--locale en_IN  --json[/dim]")
        sys.exit(0)

    url = args[0]
    locale = "en_US"
    as_json = False

    if "--locale" in args:
        idx = args.index("--locale")
        if idx + 1 < len(args):
            locale = args[idx + 1]

    if "--json" in args:
        as_json = True

    # Ensure URL has scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    creds = process_url(url, locale=locale)

    if not creds:
        sys.exit(1)

    if as_json:
        print(json.dumps(creds, indent=2))
    else:
        table = Table(
            title=f"🔐 Credentials for {url}",
            header_style="bold magenta",
            border_style="cyan",
        )
        table.add_column("Field", style="bold white", min_width=18)
        table.add_column("Value", style="green", min_width=30)

        for field, value in creds.items():
            table.add_row(field, value)

        console.print(table)


if __name__ == "__main__":
    main()
