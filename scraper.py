"""Web scraper to fetch pages and extract form fields."""

import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from models import FormField


# ---------------------------------------------------------------------------
# Page fetching
# ---------------------------------------------------------------------------

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def fetch_page(url: str, *, use_playwright: bool = False) -> str:
    """Fetch the HTML content of a page.

    Tries ``requests`` first. If *use_playwright* is True and requests finds
    no ``<form>`` elements it will retry with Playwright (headless Chromium).
    """
    html = _fetch_with_requests(url)

    if use_playwright and not _has_forms(html):
        pw_html = _fetch_with_playwright(url)
        if pw_html:
            html = pw_html

    return html


def _fetch_with_requests(url: str) -> str:
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text


def _fetch_with_playwright(url: str) -> str | None:
    """Attempt to render the page with Playwright (optional dependency)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "[yellow]Playwright not installed – skipping JS rendering.[/yellow]",
            file=sys.stderr,
        )
        return None

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30_000)
        html = page.content()
        browser.close()

    return html


def _has_forms(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    return bool(soup.find("form"))


# ---------------------------------------------------------------------------
# Form / field extraction
# ---------------------------------------------------------------------------

def extract_forms(html: str, base_url: str = "") -> list[list[FormField]]:
    """Return a list of forms, each being a list of ``FormField`` objects.

    If no ``<form>`` tags are found, falls back to collecting all top-level
    input/select/textarea elements as a single pseudo-form.
    """
    soup = BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form")

    if forms:
        return [_extract_fields_from_container(f, soup) for f in forms]

    # Fallback: no <form> wrapper – gather all input-like elements
    fields = _extract_fields_from_container(soup, soup)
    return [fields] if fields else []


def _extract_fields_from_container(
    container: Tag, root_soup: BeautifulSoup
) -> list[FormField]:
    """Extract ``FormField`` objects from a container tag."""
    fields: list[FormField] = []

    for tag_name in ("input", "textarea"):
        for el in container.find_all(tag_name):
            ff = _element_to_field(el, root_soup)
            if ff:
                fields.append(ff)

    return fields


def _element_to_field(el: Tag, root_soup: BeautifulSoup) -> FormField | None:
    """Convert a single HTML element to a ``FormField``."""
    tag = el.name
    input_type = (el.get("type") or "text").lower()

    # Skip non-writable fields
    if input_type in (
        "hidden", "submit", "button", "image", "reset",
        "checkbox", "radio", "file", "color", "range",
    ):
        return None

    name = el.get("name", "")
    field_id = el.get("id", "")
    placeholder = el.get("placeholder", "")
    autocomplete = el.get("autocomplete", "")
    required = el.has_attr("required")

    label = _find_label(el, root_soup)

    # Skip fields with no identifying info (ghost/decorative elements)
    if tag != "select" and not any([name, field_id, placeholder, label]):
        return None

    options: list[str] = []
    if tag == "select":
        options = [
            opt.get_text(strip=True)
            for opt in el.find_all("option")
            if opt.get("value", "") != ""
        ]

    return FormField(
        tag=tag,
        input_type=input_type,
        name=name,
        field_id=field_id,
        placeholder=placeholder,
        label=label,
        required=required,
        options=options,
        autocomplete=autocomplete,
    )


def _find_label(el: Tag, root_soup: BeautifulSoup) -> str:
    """Try to find the ``<label>`` text associated with an element."""
    # 1. Explicit <label for="id">
    field_id = el.get("id")
    if field_id:
        lbl = root_soup.find("label", attrs={"for": field_id})
        if lbl:
            return lbl.get_text(strip=True)

    # 2. Wrapping <label>
    parent = el.find_parent("label")
    if parent:
        # Get label text, excluding the input element's own text
        text_parts = [
            s.strip()
            for s in parent.stripped_strings
            if s.strip() and s.strip() != el.get("value", "")
        ]
        if text_parts:
            return text_parts[0]

    # 3. aria-label
    aria = el.get("aria-label")
    if aria:
        return aria

    return ""
