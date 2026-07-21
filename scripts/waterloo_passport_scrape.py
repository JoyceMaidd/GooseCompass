"""Scrape the Waterloo Passport exchange-school directory into sources.json.

Discovers every exchange school/program listed at
uwaterloo-horizons.symplicity.com and syncs scripts/sources.json to match:
newly listed schools are added, schools no longer listed are removed.
Hand-curated entries (anything not matching the Passport detail-page URL
pattern) are left untouched.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup

SOURCES_FILE = Path(__file__).parent / "sources.json"

BASE_URL = "https://uwaterloo-horizons.symplicity.com"
LIST_URL = f"{BASE_URL}/index.php"
PAGE_SIZE_PARAM = "_so_list_aat5ad5a89179cb63f89c2de5a1bb7ce758"
DETAIL_URL_PREFIX = f"{BASE_URL}/index.php?s=programs&mode=form&id="
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

ITEMS_OF_RE = re.compile(r"Items\s+[\d,]+-[\d,]+\s+of\s+([\d,]+)")
INITIAL_PAGE_SIZE = 250
MAX_PAGE_SIZE = 2000


def _fetch_school_links(client: httpx.Client) -> list[tuple[str, str]]:
    """Fetch every (id, name) pair from the Passport program listing.

    Grows the page-size query param until a single page contains every
    listed school, so the scraper keeps working if the school count grows
    well past its current ~128.

    Args:
        client: Shared HTTP client; a single client instance persists the
            cookie the site's "enable cookies" gate requires across requests.

    Returns:
        List of (school_id, school_name) pairs, deduplicated by id and
        sorted by name.

    Raises:
        RuntimeError: If the listing's total count can't be parsed, or if
            it exceeds MAX_PAGE_SIZE.
    """
    page_size = INITIAL_PAGE_SIZE
    while page_size <= MAX_PAGE_SIZE:
        resp = client.get(
            LIST_URL, params={"s": "programs", PAGE_SIZE_PARAM: page_size}
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        pairs: dict[str, str] = {}
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "mode=form" not in href or "id=" not in href:
                continue
            query = parse_qs(urlparse(href).query)
            school_id = query.get("id", [None])[0]
            if school_id:
                pairs[school_id] = a.get_text(strip=True)

        match = ITEMS_OF_RE.search(soup.get_text(" ", strip=True))
        if not match:
            raise RuntimeError(
                "Could not find an 'Items X-Y of Z' total on the Passport "
                "listing page; the page structure may have changed."
            )
        total = int(match.group(1).replace(",", ""))

        if total <= len(pairs):
            return sorted(pairs.items(), key=lambda pair: pair[1].lower())

        page_size *= 2

    raise RuntimeError(
        f"Passport listing reports more than {MAX_PAGE_SIZE} schools; "
        "increase MAX_PAGE_SIZE."
    )


def _load_existing_sources() -> list[dict]:
    """Load scripts/sources.json, tolerating a missing file.

    Returns:
        List of existing source dicts, or an empty list if the file doesn't
        exist yet.

    Raises:
        SystemExit: If the file exists but contains invalid JSON.
    """
    if not SOURCES_FILE.exists():
        return []
    try:
        return json.loads(SOURCES_FILE.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {SOURCES_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def _sync_sources(
    existing: list[dict], schools: list[tuple[str, str]]
) -> tuple[list[dict], list[str], list[str]]:
    """Merge freshly scraped schools into the existing sources list.

    Args:
        existing: Current contents of sources.json.
        schools: Freshly scraped (id, name) pairs, already sorted by name.

    Returns:
        Tuple of (new sources list, added urls, removed urls).
    """
    kept = [s for s in existing if not s.get("url", "").startswith(DETAIL_URL_PREFIX)]
    old_passport_urls = {
        s["url"] for s in existing if s.get("url", "").startswith(DETAIL_URL_PREFIX)
    }

    new_entries = [
        {"type": "web", "url": f"{DETAIL_URL_PREFIX}{school_id}"}
        for school_id, _ in schools
    ]
    new_passport_urls = {entry["url"] for entry in new_entries}

    added = sorted(new_passport_urls - old_passport_urls)
    removed = sorted(old_passport_urls - new_passport_urls)

    return kept + new_entries, added, removed


def _write_sources(sources: list[dict]) -> None:
    """Write the sources list back to sources.json, one entry per line."""
    lines = ["["]
    for i, source in enumerate(sources):
        comma = "," if i < len(sources) - 1 else ""
        lines.append(f"  {json.dumps(source)}{comma}")
    lines.append("]")
    SOURCES_FILE.write_text("\n".join(lines) + "\n")


def main() -> None:
    """Scrape the Passport school directory and sync it into sources.json."""
    parser = argparse.ArgumentParser(
        description="Scrape UWaterloo Passport exchange schools into scripts/sources.json."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the add/remove diff without writing sources.json.",
    )
    args = parser.parse_args()

    print("Fetching Passport exchange-school listing...")
    with httpx.Client(
        follow_redirects=True, headers={"User-Agent": USER_AGENT}, timeout=30
    ) as client:
        schools = _fetch_school_links(client)
    print(f"Found {len(schools)} schools.")

    existing = _load_existing_sources()
    new_sources, added, removed = _sync_sources(existing, schools)

    print(f"\n{len(added)} added, {len(removed)} removed, {len(new_sources)} total sources.")
    for url in added:
        print(f"  + {url}")
    for url in removed:
        print(f"  - {url}")

    if args.dry_run:
        print("\n-- dry-run mode: sources.json not written --")
        return

    _write_sources(new_sources)
    print(f"\nWrote {len(new_sources)} sources to {SOURCES_FILE}")


if __name__ == "__main__":
    main()
