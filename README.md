# ⚡ Internship Radar (B.Tech CSE Edition)

An autonomous daily intelligence radar for **B.Tech Computer Science & Engineering (CSE)** internships in India (Bengaluru, Hyderabad, Pune, Chennai, Gurgaon, Noida, Delhi, Mumbai + Remote).

Pulls verified tech openings from **LinkedIn**, **Unstop**, **Internshala**, and direct **Startup Careers pages**, purges non-tech noise (hotel management, HR, sales, telecalling), auto-tags technology stacks, tracks your application pipeline, and presents everything in an ultra-sleek developer dashboard on GitHub Pages.

---

## 🌟 What's New & Upgraded

1. **Multi-Source Scraping Engine**:
   - **LinkedIn Jobs**: Live guest API scraper for engineering internships (no login / credentials required).
   - **Unstop (formerly Dare2Compete)**: Official opportunities API for college engineering competitions & software internships with structured stipends and registration deadlines.
   - **Internshala**: Deep scraper strictly filtered for Computer Science.
   - **Startup Watchlist**: Career portal watcher for top startups (Zerodha, Razorpay, Postman, etc.).

2. **B.Tech CSE Relevance & Skill Engine**:
   - Strict negative blacklist purging 100+ non-tech domains (Hospitality, Human Resources, Field Sales, BDA, Telecalling, Content Writing, Graphic Design, Legal, etc.).
   - Automatic categorization into domains: `Full Stack`, `Backend`, `Frontend`, `AI / ML`, `Cloud & DevOps`, `Mobile`, `Data Engineering`, `Cybersecurity`, `Systems & Embedded`, `QA & SDET`.
   - Automatic tech stack extraction: `Python`, `React`, `Node.js`, `AWS`, `Docker`, `PostgreSQL`, `Java`, `Golang`, `Flutter`, `Kubernetes`, etc.

3. **High-Performance Developer Dashboard (`docs/index.html`)**:
   - **Obsidian / Cyber-Clean Aesthetic**: Dark mode glassmorphism with glowing radar pulse indicators.
   - **Interactive Live KPI Cards**: Total tech listings, high stipend (&ge; ₹20k/mo), urgent closing (&le; 3 days), new today.
   - **Domain Chips & Real-Time Filter**: Instant fuzzy search across titles, skills, and companies with keyboard shortcut (`Ctrl + /`).
   - **Grid vs Compact Table View**: Switch between visual cards and high-density table view.
   - **✨ In-Browser AI Pitch Assistant**: 1-click modal that generates high-converting cold email outreach and 300-char LinkedIn referral pitches tailored to the role and tech stack.
   - **In-Browser Application Tracking**: Select status (`Applied`, `OA / Test`, `Interview`, `Offer`) directly in the browser; saved instantly to `localStorage` with a 1-click "Export My Tracker" button.

4. **Zero Server / 100% Free Automation**:
   - Runs every morning via GitHub Actions (08:30 IST), scrapes, deduplicates, and commits fresh updates to GitHub Pages automatically.

---

## 🚀 Quick Setup (10 Minutes)

### 1. Push to Your GitHub Repository
```bash
git add -A
git commit -m "Upgrade to Internship Radar CSE Edition"
git push origin main
```

### 2. Enable GitHub Pages
1. Go to your repo on GitHub: **Settings &rarr; Pages**.
2. **Build and deployment &rarr; Source**: Select **"Deploy from a branch"**.
3. **Branch**: `main`, Folder: `/docs` &rarr; Click **Save**.
4. Your dashboard will be live at `https://<your-username>.github.io/<repo-name>/`.

### 3. Grant Write Permissions to GitHub Actions
1. Go to **Settings &rarr; Actions &rarr; General**.
2. Under **Workflow permissions**, choose **"Read and write permissions"**.
3. Click **Save**. (This allows the daily 08:30 IST bot to commit updated listings back to your repo).

### 4. Trigger Your First Scrape Run
1. Go to the **Actions** tab in GitHub.
2. Select **"Daily internship scrape"** on the left &rarr; Click **"Run workflow"**.

---

## 💻 Day-to-Day Usage

### 🌐 Using the Web Dashboard
Just open your GitHub Pages URL:
- Filter by your favorite tech stack (`React`, `Python`, `Docker`, `AI/ML`).
- Click **"✨ AI Pitch"** on any job to copy an instant tailored cold email.
- Change status in the dropdown (saved locally in your browser).
- Click **"Export My Tracker"** anytime to download your updated `applications.json`.

### ⌨️ Using the CLI
```bash
# View summary statistics of all tech domains and application pipeline
python track.py stats

# List verified CSE internships (soonest deadline first)
python track.py list

# Search for specific tech skills or companies
python track.py search python
python track.py search razorpay

# View full job details & history
python track.py show <id>

# Track your application progress
python track.py apply <id> -n "Applied via referral"
python track.py status <id> interview -n "Technical round on Friday"

# Sync web-exported applications back into git
python track.py sync-web applications.json
```

---

## 🛠️ Configuration

Tune settings in [`config/settings.py`](config/settings.py):
- `TARGET_CITIES`: Target cities for search queries (`bangalore`, `hyderabad`, `pune`, `gurgaon`, etc.).
- `ENABLED_SOURCES`: Choose active scrapers (`["linkedin", "unstop", "internshala", "watchlist"]`).
- `MIN_STIPEND`: Filter out stipends below a minimum threshold (0 = keep all).
- `DEADLINE_WARNING_DAYS`: Days threshold for the urgent closing badge (default: 3 days).

Add custom startup career pages in [`config/watchlist.json`](config/watchlist.json):
```json
{
  "companies": [
    { "name": "Zerodha", "careers_url": "https://zerodha.com/careers/" },
    { "name": "Razorpay", "careers_url": "https://razorpay.com/jobs/" }
  ]
}
```

---

## 📁 Project Architecture

```
internship-tracker/
├── .github/workflows/
│   └── daily.yml             # Daily automated cron runner (08:30 IST)
├── config/
│   ├── settings.py           # Targets, cities, keywords, rate limits
│   └── watchlist.json        # Startup careers pages to monitor
├── data/
│   ├── internships.json      # Permanent store of verified CSE internships
│   ├── applications.json     # Application history & statuses
│   └── purged_non_cse.json   # Archived non-tech records (HR, hotel mgmt, etc.)
├── docs/
│   └── index.html            # High-performance, eye-candy dashboard
├── scrapers/
│   ├── base.py               # Rate-limited HTTP client & filter adapter
│   ├── cse_filter.py         # Relevance classifier & tech tagger
│   ├── linkedin.py           # LinkedIn guest search API scraper
│   ├── unstop.py             # Unstop opportunities API scraper
│   ├── internshala.py        # Internshala CS scraper
│   └── watchlist.py          # Career page diff watcher
├── generate_dashboard.py     # Static dashboard compiler
├── run_all.py                # Pipeline orchestrator
├── storage.py                # JSON store & database cleaner
└── track.py                  # CLI tracker & web sync tool
```
