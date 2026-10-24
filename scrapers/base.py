import re
import time
import logging
import requests

from config.settings import (
    REQUEST_HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY, MIN_STIPEND,
)
from scrapers.cse_filter import classify_cse_role

logger = logging.getLogger("scraper.base")


def polite_get(url, session=None, retries=3, custom_headers=None):
    """GET a URL with browser-like headers, retrying on transient failure."""
    sess = session or requests
    headers = dict(REQUEST_HEADERS)
    if custom_headers:
        headers.update(custom_headers)

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = sess.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                time.sleep(REQUEST_DELAY)
                return resp
            logger.warning("GET %s -> HTTP %s (attempt %d/%d)", url, resp.status_code, attempt, retries)
            last_err = f"HTTP {resp.status_code}"
        except requests.RequestException as e:
            logger.warning("GET %s failed (attempt %d/%d): %s", url, attempt, retries, e)
            last_err = str(e)
        time.sleep(REQUEST_DELAY * attempt)
    logger.error("Giving up on %s: %s", url, last_err)
    return None


def extract_stipend_number(stipend_text: str) -> int:
    """'₹ 10,000-15,000 /month' -> 10000 (lower bound). Handles commas, /week, and LPA."""
    if not stipend_text:
        return 0
    text = stipend_text.lower()
    if "unpaid" in text or "free" in text or "volunteer" in text:
        return 0

    cleaned = text.replace(",", "")
    numbers = [int(n) for n in re.findall(r"\d+", cleaned)]
    if not numbers:
        return 0

    amount = numbers[0]
    # If per week, convert to approximate monthly (* 4)
    if "week" in text:
        amount *= 4
    # If in thousands shorthand (e.g. 15k)
    elif "k" in text and amount < 1000:
        amount *= 1000
    # If annual/LPA (e.g., 3-5 LPA)
    elif "lpa" in text or "lakh" in text:
        if amount <= 50:
            amount = int((amount * 100000) / 12)

    return amount


def passes_filters(title: str, description: str = "", stipend_amount: int = 0) -> tuple[bool, dict]:
    """
    Checks if a job listing qualifies as a B.Tech CSE internship.
    Returns: (passes: bool, classification_dict)
    """
    classification = classify_cse_role(title, description)
    if not classification["is_cse"]:
        return False, classification

    if MIN_STIPEND and stipend_amount and stipend_amount < MIN_STIPEND:
        return False, classification

    return True, classification
