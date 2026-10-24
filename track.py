"""
Application tracker CLI.
Track applications, query tech roles, inspect pipeline stats, and sync web updates.

Examples:
  python track.py list                          # list active CSE opportunities
  python track.py list --status applied         # only roles you've applied to
  python track.py stats                         # pipeline & domain breakdown
  python track.py search python                 # find an internship by keyword
  python track.py show ab12cd34ef               # full details + history for one id
  python track.py apply ab12cd34ef -n "referral"
  python track.py status ab12cd34ef interview -n "Interview on Friday"
  python track.py sync-web exported.json        # sync changes from web dashboard
"""
import argparse
import textwrap

from storage import (
    load_internships, load_applications, set_status,
    sync_web_applications, VALID_STATUSES
)


def cmd_list(args):
    internships = load_internships()
    applications = load_applications()

    rows = []
    for iid, rec in internships.items():
        status = applications.get(iid, {}).get("status", "not_applied")
        if args.status and status != args.status:
            continue
        rows.append((iid, rec, status))

    rows.sort(key=lambda r: r[1].get("apply_by") or "9999")

    if not rows:
        print("No matching internships.")
        return

    for iid, rec, status in rows:
        domain = rec.get("domain", "Tech")
        tags = ", ".join(rec.get("tags", []))
        print(f"[{iid}] [{domain}] {rec['title']} @ {rec['company']}")
        print(f"    {rec.get('location','?')} | {rec.get('stipend_text','?')} | "
              f"Apply: {rec.get('apply_by','?')} | Status: {status} | Source: {rec.get('source','?')}")
        if tags:
            print(f"    Tech: {tags}")


def cmd_stats(args):
    internships = load_internships()
    applications = load_applications()

    print(f"\n================ INTERNSHIP RADAR STATS ================")
    print(f"Total Verified CSE Internships : {len(internships)}")

    domains = {}
    sources = {}
    for r in internships.values():
        dom = r.get("domain", "Core Tech")
        src = r.get("source", "unknown")
        domains[dom] = domains.get(dom, 0) + 1
        sources[src] = sources.get(src, 0) + 1

    print("\n--- Domain Breakdown ---")
    for d, count in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {d:22}: {count}")

    print("\n--- Source Distribution ---")
    for s, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {s.capitalize():22}: {count}")

    print("\n--- Application Pipeline ---")
    status_counts = {}
    for a in applications.values():
        st = a.get("status", "not_applied")
        status_counts[st] = status_counts.get(st, 0) + 1

    for st in VALID_STATUSES:
        if st in status_counts:
            print(f"  {st.replace('_', ' ').title():22}: {status_counts[st]}")
    print("========================================================\n")


def cmd_search(args):
    internships = load_internships()
    q = args.query.lower()
    hits = [(iid, r) for iid, r in internships.items()
            if q in r.get("title", "").lower() 
            or q in r.get("company", "").lower() 
            or any(q in t.lower() for t in r.get("tags", []))]
    if not hits:
        print("No matches found.")
        return
    for iid, r in hits:
        tags = f" ({', '.join(r.get('tags', []))})" if r.get("tags") else ""
        print(f"[{iid}] [{r.get('domain','Tech')}] {r['title']} @ {r['company']}{tags}")
        print(f"    Link: {r.get('link','')}")


def cmd_show(args):
    internships = load_internships()
    applications = load_applications()
    rec = internships.get(args.id)
    if not rec:
        print(f"No internship found with id {args.id}")
        return
    for k, v in rec.items():
        print(f"{k}: {textwrap.shorten(str(v), 200)}")
    app = applications.get(args.id)
    if app:
        print("\n--- Application History ---")
        for h in app.get("history", []):
            ts = h.get("timestamp") or h.get("at", "")
            print(f"  {ts}: {h['status']}" + (f" - {h['note']}" if h.get("note") else ""))


def cmd_apply(args):
    rec = set_status(args.id, "applied", note=args.note or "")
    print(f"Marked {args.id} as applied. Total history entries: {len(rec['history'])}")


def cmd_status(args):
    rec = set_status(args.id, args.new_status, note=args.note or "")
    print(f"Updated {args.id} -> {args.new_status}")


def cmd_sync_web(args):
    res = sync_web_applications(args.file)
    print(f"Successfully synced {res['synced']} applications from {args.file} (Total tracked: {res['total']})")


def main():
    parser = argparse.ArgumentParser(description="Internship Radar Tracker CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List internships")
    p_list.add_argument("--status", choices=VALID_STATUSES)
    p_list.set_defaults(func=cmd_list)

    p_stats = sub.add_parser("stats", help="Display pipeline statistics")
    p_stats.set_defaults(func=cmd_stats)

    p_search = sub.add_parser("search", help="Search by title, company, or tech skill")
    p_search.add_argument("query")
    p_search.set_defaults(func=cmd_search)

    p_show = sub.add_parser("show", help="Show full details + history for one id")
    p_show.add_argument("id")
    p_show.set_defaults(func=cmd_show)

    p_apply = sub.add_parser("apply", help="Mark an internship as applied")
    p_apply.add_argument("id")
    p_apply.add_argument("-n", "--note", default="")
    p_apply.set_defaults(func=cmd_apply)

    p_status = sub.add_parser("status", help="Set an arbitrary status")
    p_status.add_argument("id")
    p_status.add_argument("new_status", choices=VALID_STATUSES)
    p_status.add_argument("-n", "--note", default="")
    p_status.set_defaults(func=cmd_status)

    p_sync = sub.add_parser("sync-web", help="Sync applications.json exported from web dashboard")
    p_sync.add_argument("file", help="Path to exported applications.json")
    p_sync.set_defaults(func=cmd_sync_web)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
