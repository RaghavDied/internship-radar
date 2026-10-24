"""
Master Execution Pipeline for Internship Radar.
Runs all active scrapers (LinkedIn, Unstop, Internshala, Watchlist),
merges results, validates B.Tech CSE relevance, and triggers dashboard generation.
"""
import logging
import sys
import time

from config.settings import ENABLED_SOURCES
from scrapers import internshala, linkedin, unstop, watchlist
from storage import upsert_internships, clean_and_enrich_database
import generate_dashboard

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("run_all")


SCRAPER_REGISTRY = {
    "linkedin": linkedin.scrape,
    "unstop": unstop.scrape,
    "internshala": internshala.scrape,
    "watchlist": watchlist.scrape,
}


def run_scrapers() -> list[dict]:
    all_listings = []
    failures = []

    for name in ENABLED_SOURCES:
        scraper_fn = SCRAPER_REGISTRY.get(name)
        if not scraper_fn:
            logger.warning("Scraper '%s' is not registered. Skipping.", name)
            continue

        start_time = time.time()
        logger.info("Starting scraper: %s ...", name.upper())
        try:
            listings = scraper_fn()
            duration = round(time.time() - start_time, 2)
            logger.info("Scraper %s finished in %ss: %d listings collected", name.upper(), duration, len(listings))
            all_listings.extend(listings)
        except Exception as e:
            logger.exception("Scraper %s failed with error: %s", name, e)
            failures.append(name)

    return all_listings, failures


def main():
    logger.info("Initializing Daily Internship Scrape & Processing...")

    all_listings, failures = run_scrapers()

    if all_listings:
        stats = upsert_internships(all_listings)
        logger.info(
            "Upsert complete: %d new CSE listings, %d updated, %d rejected non-tech, %d total in database",
            stats["new"], stats["updated"], stats.get("rejected_non_cse", 0), stats["total"]
        )
    else:
        logger.warning("No listings collected this run.")

    # Run database clean & enrichment check
    cleanup_stats = clean_and_enrich_database()
    logger.info("Database verification: %d active CSE listings maintained", cleanup_stats["kept_cse"])

    # Automatically generate updated dashboard
    logger.info("Building refreshed dashboard docs/index.html ...")
    generate_dashboard.build()

    if failures:
        logger.warning("Completed with partial failures on scrapers: %s", ", ".join(failures))
        # Keep non-zero return code for GitHub Actions warning visibility
        return 1
    
    logger.info("All pipelines completed successfully.")
    return 0


if __name__ == "__main__":
    code = main()
    sys.exit(code)
