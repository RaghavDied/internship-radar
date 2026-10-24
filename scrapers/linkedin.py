"""
LinkedIn Jobs Guest Scraper.
Scrapes real-time tech internships from LinkedIn's public job search API
without requiring credentials or cookies.
"""
import logging
import time
import urllib.parse
from bs4 import BeautifulSoup

from config.settings import LINKEDIN_SEARCH_QUERIES
from scrapers.base import polite_get, passes_filters
from storage import make_id

logger = logging.getLogger("scraper.linkedin")

SOURCE_NAME = "linkedin"
BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


def scrape_query(query: str, location: str = "India", max_pages: int = 1) -> list[dict]:
    """Scrape LinkedIn guest job cards for a given query."""
    results = []
    
    for page in range(max_pages):
        start = page * 10
        params = {
            "keywords": query,
            "location": location,
            "f_TPR": "r604800", # Past 7 days
            "start": start
        }
        url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
        resp = polite_get(url)
        if resp is None:
            # Hit rate limit or error, stop pagination for this query
            break

        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select("div.base-card, li")
        if not cards:
            break

        for card in cards:
            try:
                title_el = card.select_one(".base-search-card__title")
                company_el = card.select_one(".base-search-card__subtitle")
                loc_el = card.select_one(".job-search-card__location")
                link_el = card.select_one("a.base-card__full-link, a.base-search-card--link")
                time_el = card.select_one("time")

                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                company = company_el.get_text(strip=True) if company_el else "Unknown"
                location_text = loc_el.get_text(strip=True) if loc_el else location
                raw_link = link_el.get("href", "")
                clean_link = raw_link.split("?")[0] if raw_link else ""
                posted = time_el.get("datetime") or time_el.get_text(strip=True) if time_el else ""

                if not clean_link or not title:
                    continue

                # Run CSE relevance classification
                passed, classification = passes_filters(title, description="")
                if not passed:
                    continue

                results.append({
                    "id": make_id(clean_link, title, company),
                    "title": title,
                    "company": company,
                    "location": location_text,
                    "stipend_text": "Competitive / Unspecified",
                    "stipend_amount": 0,
                    "duration": "2 - 6 Months",
                    "apply_by": "Rolling / Urgent",
                    "posted": posted,
                    "link": clean_link,
                    "description": f"LinkedIn Tech Opening: {title} at {company}",
                    "source": SOURCE_NAME,
                    "domain": classification["domain"],
                    "tags": classification["tags"],
                    "cse_score": classification["score"],
                })
            except Exception as e:
                logger.debug("Failed parsing LinkedIn card: %s", e)
                continue

    return results


def scrape() -> list[dict]:
    """Run LinkedIn scraper across target tech queries."""
    all_results = []
    seen_ids = set()

    # Prioritize key tech queries to stay within polite rate limits
    queries = LINKEDIN_SEARCH_QUERIES[:5]
    for q in queries:
        logger.info("Scraping LinkedIn for: '%s'", q)
        query_results = scrape_query(q, max_pages=1)
        for r in query_results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                all_results.append(r)
        time.sleep(2) # polite pause between queries

    logger.info("LinkedIn scrape finished: %d relevant tech internships found", len(all_results))
    return all_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = scrape()
    print(f"Total LinkedIn items: {len(data)}")
    for d in data[:3]:
        print(f"[{d['domain']}] {d['title']} @ {d['company']} -> {d['link']}")
