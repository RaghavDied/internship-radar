"""
Storage Engine for Internship Radar.
Manages JSON-backed listings, applications, CSE validation, and cleanup.
"""
import json
import os
import hashlib
from datetime import datetime, timezone

from config.settings import INTERNSHIPS_FILE, APPLICATIONS_FILE, DATA_DIR
from scrapers.cse_filter import classify_cse_role


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def make_id(link: str, title: str = "", company: str = "") -> str:
    """Stable hash ID for a listing."""
    basis = link.strip().lower() if link else f"{title}|{company}".strip().lower()
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_internships() -> dict:
    """Returns {id: record} dict."""
    _ensure_data_dir()
    if not os.path.exists(INTERNSHIPS_FILE):
        return {}
    with open(INTERNSHIPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_internships(records: dict):
    _ensure_data_dir()
    with open(INTERNSHIPS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False, sort_keys=True)


def clean_and_enrich_database() -> dict:
    """
    Cleans existing database:
    - Purges out non-CSE roles (hotel management, HR, sales, accounts, etc.)
    - Enriches existing tech roles with domain, tags, and cse_score
    - Archives removed listings to data/purged_non_cse.json
    Returns cleanup statistics.
    """
    records = load_internships()
    total_before = len(records)
    cleaned_records = {}
    purged_records = {}

    for iid, item in records.items():
        title = item.get("title", "")
        desc = item.get("description", "")
        classification = classify_cse_role(title, desc)

        if classification["is_cse"]:
            item["domain"] = classification["domain"]
            item["tags"] = classification["tags"]
            item["cse_score"] = classification["score"]
            cleaned_records[iid] = item
        else:
            purged_records[iid] = item

    save_internships(cleaned_records)

    if purged_records:
        archive_path = os.path.join(DATA_DIR, "purged_non_cse.json")
        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(purged_records, f, indent=2, ensure_ascii=False)

    return {
        "before": total_before,
        "kept_cse": len(cleaned_records),
        "purged_non_cse": len(purged_records),
    }


def upsert_internships(new_listings: list) -> dict:
    """
    Merge freshly scraped listings into the store.
    - Only accepts listings that qualify as CSE.
    - New listing -> added with first_seen_at = now.
    - Existing listing -> fields refreshed, preserving first_seen_at.
    """
    existing = load_internships()
    new_count = 0
    updated_count = 0
    rejected_non_cse = 0
    ts = now_iso()

    for listing in new_listings:
        if not listing.get("domain") or not listing.get("cse_score"):
            classification = classify_cse_role(listing.get("title", ""), listing.get("description", ""))
            if not classification["is_cse"]:
                rejected_non_cse += 1
                continue
            listing["domain"] = classification["domain"]
            listing["tags"] = classification["tags"]
            listing["cse_score"] = classification["score"]

        rid = listing["id"]
        if rid in existing:
            preserved_first_seen = existing[rid].get("first_seen_at", ts)
            existing[rid].update(listing)
            existing[rid]["first_seen_at"] = preserved_first_seen
            existing[rid]["last_seen_at"] = ts
            updated_count += 1
        else:
            listing["first_seen_at"] = ts
            listing["last_seen_at"] = ts
            existing[rid] = listing
            new_count += 1

    save_internships(existing)
    return {
        "new": new_count,
        "updated": updated_count,
        "rejected_non_cse": rejected_non_cse,
        "total": len(existing)
    }


def load_applications() -> dict:
    """Returns {internship_id: {status, notes, history: [...]}}"""
    _ensure_data_dir()
    if not os.path.exists(APPLICATIONS_FILE):
        return {}
    with open(APPLICATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_applications(records: dict):
    _ensure_data_dir()
    with open(APPLICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False, sort_keys=True)


VALID_STATUSES = [
    "not_applied", "applied", "online_test", "interview",
    "offer", "rejected", "withdrawn",
]


def set_status(internship_id: str, status: str, note: str = "") -> dict:
    if status not in VALID_STATUSES:
        raise ValueError(f"Unknown status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")
    apps = load_applications()
    record = apps.setdefault(internship_id, {
        "status": "not_applied",
        "notes": "",
        "updated_at": now_iso(),
        "history": [],
    })
    record["status"] = status
    if note:
        record["notes"] = note
    record["updated_at"] = now_iso()
    record["history"].append({
        "status": status,
        "timestamp": now_iso(),
        "note": note,
    })
    save_applications(apps)
    return record


def sync_web_applications(file_path: str) -> dict:
    """Import and merge applications.json exported from browser."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")
    with open(file_path, "r", encoding="utf-8") as f:
        web_data = json.load(f)
    
    current_apps = load_applications()
    imported_count = 0
    for iid, val in web_data.items():
        st = val.get("status") if isinstance(val, dict) else val
        if st and st in VALID_STATUSES and st != "not_applied":
            set_status(iid, st, note="Synced from web dashboard")
            imported_count += 1
    return {"synced": imported_count, "total": len(load_applications())}
