#!/usr/bin/env python3
"""
Import Google Scholar publications into Jekyll `_publications/` for Academic Pages.

Usage:
  python scripts/import_scholar.py --user fKuqskgAAAAJ [--hl zh-CN] [--max 200]

Requirements:
  pip install scholarly==1.7.11 python-slugify==8.0.4

Notes:
- Scholar can throttle or require CAPTCHA. If blocked, try again later or with a VPN.
- Dates on Scholar are often year-only; we default missing month/day to 01-01.
"""
import argparse
import os
import re
from datetime import datetime
from pathlib import Path

from slugify import slugify
from scholarly import scholarly

ROOT = Path(__file__).resolve().parents[1]
PUB_DIR = ROOT / "_publications"


def html_escape(text: str) -> str:
    table = {"&": "&amp;", '"': "&quot;", "'": "&apos;"}
    return "".join(table.get(c, c) for c in text)


def safe_date(year: int | None) -> str:
    if not year:
        return "1900-01-01"
    try:
        return f"{int(year):04d}-01-01"
    except Exception:
        return "1900-01-01"


def to_markdown(item: dict) -> tuple[str, str]:
    """Return (filename, markdown_contents)."""
    title = item.get("bib", {}).get("title") or "Untitled"
    venue = item.get("bib", {}).get("venue") or item.get("bib", {}).get("journal") or ""
    year = item.get("bib", {}).get("pub_year")
    url = item.get("eprint_url") or item.get("pub_url") or ""

    authors = item.get("bib", {}).get("author") or item.get("bib", {}).get("authors") or ""
    if isinstance(authors, list):
        authors_str = ", ".join(authors)
    else:
        authors_str = str(authors)

    # Basic citation string
    citation_bits = [authors_str, f"{year}" if year else None, title, venue]
    citation = ". ".join([b for b in citation_bits if b])

    date = safe_date(year)

    url_slug = slugify(title)[:80]
    md_filename = f"{date}-{url_slug}.md"
    html_filename = f"{date}-{url_slug}"

    md = []
    md.append("---")
    md.append(f"title: \"{html_escape(title)}\"")
    md.append("collection: publications")
    md.append(f"permalink: /publication/{html_filename}")
    md.append(f"date: {date}")
    if venue:
        md.append(f"venue: '{html_escape(venue)}'")
    if url:
        md.append(f"paperurl: '{url}'")
    if citation:
        md.append(f"citation: '{html_escape(citation)}'")
    md.append("---\n")

    if url:
        md.append(f"<a href='{url}'>Download or view</a>\n")

    return md_filename, "\n".join(md)


def fetch_publications(user: str, max_pubs: int | None = None, hl: str | None = None):
    # Note: scholarly 1.7.x does not expose a set_lang API; hl is accepted but unused.
    author = scholarly.search_author_id(user)
    author = scholarly.fill(author, sections=['publications'])

    pubs = author.get('publications', [])
    results = []
    for i, p in enumerate(pubs):
        if max_pubs is not None and i >= max_pubs:
            break
        try:
            filled = scholarly.fill(p)
            results.append(filled)
        except Exception:
            # Skip problematic entries
            continue
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--user', required=True, help='Google Scholar user id (the value of user=...)')
    ap.add_argument('--max', type=int, default=None, help='Max number of publications to import')
    ap.add_argument('--hl', default=None, help='Scholar language, e.g., en or zh-CN')
    args = ap.parse_args()

    PUB_DIR.mkdir(parents=True, exist_ok=True)

    pubs = fetch_publications(args.user, args.max, args.hl)
    created = 0
    for pub in pubs:
        fn, md = to_markdown(pub)
        (PUB_DIR / fn).write_text(md, encoding='utf-8')
        created += 1

    print(f"Wrote {created} publication files to {PUB_DIR}")


if __name__ == "__main__":
    main()
