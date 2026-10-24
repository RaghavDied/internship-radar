"""
Central configuration for Internship Radar.
Tuned specifically for B.Tech Computer Science & Engineering (CSE) students.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

INTERNSHIPS_FILE = os.path.join(DATA_DIR, "internships.json")
APPLICATIONS_FILE = os.path.join(DATA_DIR, "applications.json")
WATCHLIST_FILE = os.path.join(BASE_DIR, "config", "watchlist.json")

# Enabled data scrapers
ENABLED_SOURCES = [
    "linkedin",
    "unstop",
    "internshala",
    "watchlist",
]

# Cities you're targeting (used to build search queries)
TARGET_CITIES = [
    "bangalore",   # Bengaluru
    "hyderabad",
    "pune",
    "chennai",
    "gurgaon",
    "noida",
    "delhi",
    "mumbai",
]

# Include remote / work-from-home tech internships
INCLUDE_WORK_FROM_HOME = True

# Internshala category slugs to pull
INTERNSHALA_CATEGORIES = [
    "computer-science",
    "web-development",
    "mobile-app-development",
    "artificial-intelligence-ai",
    "data-science",
]

# LinkedIn target keywords for public guest search
LINKEDIN_SEARCH_QUERIES = [
    "Software Engineer Intern",
    "Frontend Developer Intern",
    "Backend Developer Intern",
    "Full Stack Intern",
    "Data Science Intern",
    "Machine Learning Intern",
    "DevOps Intern",
    "Android Developer Intern",
]

# Unstop search terms
UNSTOP_SEARCH_TERMS = [
    "software",
    "frontend",
    "backend",
    "full stack",
    "data science",
    "machine learning",
    "python",
    "web development",
]

# Minimum stipend in INR/month (0 = don't filter out, will still sort)
MIN_STIPEND = 0

# How many days out counts as "deadline approaching" (red badge in dashboard)
DEADLINE_WARNING_DAYS = 3

# Prune or archive listings whose deadlines expired more than X days ago
EXPIRED_GRACE_DAYS = 21

# Browser-like headers for scraping
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 15  # seconds
REQUEST_DELAY = 1.2   # seconds between requests to avoid rate limits

# Internshala detail deadline fetch settings
FETCH_DEADLINE_DETAIL = True
MAX_DETAIL_FETCHES_PER_RUN = 50
