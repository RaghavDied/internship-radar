"""
Watchlist scraper: watches specific startup careers pages defined in config/watchlist.json.
Flags when careers pages mention internships and extracts relevant tech indicators.
"""
import hashlib
import json
import logging
import os
import re

from bs4 import BeautifulSoup

from config.settings import WATCHLIST_FILE, BASE_DIR
from scrapers.base import polite_get
from scrapers.cse_filter import classify_cse_role
from storage import make_id

logger = logging.getLogger("scraper.watchlist")

SOURCE_NAME = "watchlist"
SNAPSHOT_FILE = os.path.join(BASE_DIR, "data", "watchlist_snapshots.json")

INTERN_KEYWORDS = re.compile(r"\bintern(ship)?s?\b", re.IGNORECASE)


def _load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return []
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("companies", [])


def _load_snapshots():
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_snapshots(snapshots):
    os.makedirs(os.path.dirname(SNAPSHOT_FILE), exist_ok=True)
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshots, f, indent=2)


def _page_signature(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def scrape() -> list:
    companies = _load_watchlist()
    if not companies:
        logger.info("Watchlist is empty - add companies to config/watchlist.json")
        return []

    snapshots = _load_snapshots()
    results = []

    for entry in companies:
        name = entry.get("name", "Unknown company")
        url = entry.get("careers_url")
        if not url:
            continue

        resp = polite_get(url)
        if resp is None:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        page_text = soup.get_text(separator=" ", strip=True)
        mentions_intern = bool(INTERN_KEYWORDS.search(page_text))
        sig = _page_signature(page_text)

        prev_sig = snapshots.get(url, {}).get("signature")
        changed = sig != prev_sig
        snapshots[url] = {"signature": sig}

        if mentions_intern:
            # Grab snippet around match
            match = INTERN_KEYWORDS.search(page_text)
            start = max(0, match.start() - 100)
            end = min(len(page_text), match.end() + 100)
            snippet = page_text[start:end].strip()

            classification = classify_cse_role(f"Engineering Intern at {name}", snippet)

            results.append({
                "id": make_id(url + ("#changed" if changed else ""), name, "watchlist"),
                "title": f"Internship Opportunity at {name}" + (" (New Activity)" if changed else ""),
                "company": name,
                "location": "Careers Portal / Remote",
                "stipend_text": "Check Company Careers Page",
                "stipend_amount": 0,
                "duration": "Check Portal",
                "apply_by": "Rolling / ASAP",
                "posted": "Active",
                "link": url,
                "description": f"Careers page mention: {snippet[:200]}...",
                "source": SOURCE_NAME,
                "domain": classification["domain"] if classification["is_cse"] else "Core Software Dev",
                "tags": classification["tags"],
                "cse_score": max(classification["score"], 70),
            })

    _save_snapshots(snapshots)
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Scraping watchlist...")
    items = scrape()
    print(f"Found {len(items)} watchlist opportunities")
