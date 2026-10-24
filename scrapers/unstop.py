"""
Unstop (formerly Dare2Compete) Scraper.
Scrapes tech and engineering internships from Unstop's public opportunities API.
"""
import logging
import urllib.parse
from datetime import datetime

from config.settings import UNSTOP_SEARCH_TERMS
from scrapers.base import polite_get, passes_filters
from storage import make_id

logger = logging.getLogger("scraper.unstop")

SOURCE_NAME = "unstop"
BASE_API = "https://unstop.com/api/public/opportunity/search-result"


def parse_unstop_item(item: dict) -> dict | None:
    try:
        title = item.get("title", "").strip()
        org = item.get("organisation", {})
        company = org.get("name", "Unknown Company").strip() if org else "Unknown Company"
        
        rel_url = item.get("public_url") or item.get("seo_url") or ""
        if not rel_url or not title:
            return None
        link = f"https://unstop.com/{rel_url.lstrip('/')}"

        # Location extraction
        locations_list = item.get("locations") or []
        cities = []
        for loc in locations_list:
            if isinstance(loc, dict) and loc.get("city"):
                cities.append(loc["city"])
        location = ", ".join(cities) if cities else "India / Remote"

        # Stipend extraction
        job_detail = item.get("jobDetail") or {}
        min_sal = job_detail.get("min_salary") or 0
        max_sal = job_detail.get("max_salary") or 0
        stipend_amount = min_sal if min_sal else max_sal
        
        if min_sal and max_sal and min_sal != max_sal:
            stipend_text = f"₹{min_sal:,} - ₹{max_sal:,} /month"
        elif min_sal or max_sal:
            stipend_text = f"₹{stipend_amount:,} /month"
        elif job_detail.get("paid_unpaid") == "unpaid":
            stipend_text = "Unpaid"
        else:
            stipend_text = "Competitive / Performance Based"

        # Deadline extraction
        regn_req = item.get("regnRequirements") or {}
        end_dt_raw = regn_req.get("end_regn_dt") or item.get("end_date") or ""
        apply_by = ""
        if end_dt_raw:
            try:
                dt = datetime.fromisoformat(end_dt_raw.replace("Z", "+00:00"))
                apply_by = dt.strftime("%d %b %Y")
            except Exception:
                apply_by = end_dt_raw[:10]

        # Extract skills
        skills = item.get("required_skills") or []
        skill_names = []
        for s in skills:
            if isinstance(s, dict) and s.get("name"):
                skill_names.append(s["name"])
            elif isinstance(s, str):
                skill_names.append(s)
        
        description = f"{title} at {company}. Skills: {', '.join(skill_names)}"

        # Evaluate against CSE relevance filter
        passed, classification = passes_filters(title, description=description, stipend_amount=stipend_amount)
        if not passed:
            return None

        # Merge extracted skill names with classified tags
        merged_tags = list(dict.fromkeys(classification["tags"] + skill_names[:3]))

        return {
            "id": make_id(link, title, company),
            "title": title,
            "company": company,
            "location": location,
            "stipend_text": stipend_text,
            "stipend_amount": stipend_amount,
            "duration": "2 - 6 Months",
            "apply_by": apply_by or "Open",
            "posted": (item.get("updated_at") or "")[:10],
            "link": link,
            "description": description,
            "source": SOURCE_NAME,
            "domain": classification["domain"],
            "tags": merged_tags[:5],
            "cse_score": classification["score"],
        }
    except Exception as e:
        logger.debug("Failed parsing Unstop opportunity: %s", e)
        return None


def scrape() -> list[dict]:
    """Scrape Unstop for engineering and software internships."""
    all_results = []
    seen_ids = set()

    for term in UNSTOP_SEARCH_TERMS[:5]:
        params = {
            "opportunity": "internships",
            "page": 1,
            "per_page": 20,
            "oppstatus": "open",
            "searchTerm": term
        }
        url = f"{BASE_API}?{urllib.parse.urlencode(params)}"
        resp = polite_get(url)
        if resp is None:
            continue

        try:
            payload = resp.json()
            items = payload.get("data", {}).get("data", [])
            for item in items:
                parsed = parse_unstop_item(item)
                if parsed and parsed["id"] not in seen_ids:
                    seen_ids.add(parsed["id"])
                    all_results.append(parsed)
        except Exception as e:
            logger.warning("Failed parsing Unstop JSON response for term '%s': %s", term, e)

    logger.info("Unstop scrape finished: %d relevant tech internships found", len(all_results))
    return all_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = scrape()
    print(f"Total Unstop items: {len(data)}")
    for d in data[:3]:
        clean_stipend = d['stipend_text'].replace("\u20b9", "Rs. ")
        print(f"[{d['domain']}] {d['title']} @ {d['company']} | Stipend: {clean_stipend} | Deadline: {d['apply_by']}")
