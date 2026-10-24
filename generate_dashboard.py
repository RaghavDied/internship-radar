"""
Generates the modern, high-performance static dashboard in docs/index.html.
Engineered with an ultra-sleek obsidian/neon developer theme, real-time filters,
in-browser application tracking, and an AI cold pitch & referral generator.
"""
import json
import os
import re
from datetime import datetime, timezone, date, timedelta

from dateutil import parser as dateutil_parser

from config.settings import DOCS_DIR, DEADLINE_WARNING_DAYS
from storage import load_internships, load_applications

STATUS_LABELS = {
    "not_applied": "Not Applied",
    "applied": "Applied",
    "online_test": "OA / Test",
    "interview": "Interview",
    "offer": "Offer Received 🎉",
    "rejected": "Rejected",
    "withdrawn": "Withdrawn",
}

STATUS_COLORS = {
    "not_applied": "badge-neutral",
    "applied": "badge-blue",
    "online_test": "badge-purple",
    "interview": "badge-amber",
    "offer": "badge-emerald",
    "rejected": "badge-rose",
    "withdrawn": "badge-neutral",
}

def _parse_deadline_to_iso(apply_by_text: str):
    if not apply_by_text or apply_by_text.strip().lower() in ("unknown", "not specified", "open", "rolling", "asap", ""):
        return None
    cleaned = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", apply_by_text, flags=re.IGNORECASE)
    try:
        parsed = dateutil_parser.parse(cleaned, fuzzy=True, default=datetime(date.today().year, 1, 1))
    except (ValueError, OverflowError):
        return None
    parsed_date = parsed.date()
    # If deadline parsed in distant past, handle rolling year
    if parsed_date < date.today() - timedelta(days=45):
        parsed_date = parsed_date.replace(year=parsed_date.year + 1)
    return parsed_date.isoformat()


DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Internship Radar | B.Tech CSE Internship Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
            display: ['Plus Jakarta Sans', 'sans-serif'],
          },
          colors: {
            brand: {
              50: '#ECFEFF',
              100: '#CFFAFE',
              400: '#22D3EE',
              500: '#06B6D4',
              DEFAULT: '#00F0FF',
            },
            dark: {
              base: '#070A0F',
              surface: '#0D131F',
              card: '#121A2B',
              border: 'rgba(255, 255, 255, 0.08)',
              hover: '#192338',
            }
          }
        }
      }
    }
  </script>
  <style>
    body {
      background-color: #070A0F;
      background-image: 
        radial-gradient(at 0% 0%, rgba(6, 182, 212, 0.07) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.07) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
      background-attachment: fixed;
      color: #F1F5F9;
    }
    .custom-scrollbar::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
      background: #0D131F;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background: #1E293B;
      border-radius: 3px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
      background: #334155;
    }
    .glass-card {
      background: rgba(18, 26, 43, 0.75);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.07);
    }
    .glass-card:hover {
      border-color: rgba(6, 182, 212, 0.35);
      box-shadow: 0 8px 30px rgba(0, 240, 255, 0.06);
    }
    .glass-panel {
      background: rgba(13, 19, 31, 0.85);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .pulse-dot {
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
      100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
  </style>
</head>
<body class="min-h-screen flex flex-col font-sans selection:bg-brand selection:text-black custom-scrollbar">

  <!-- TOP ANNOUNCEMENT & RADAR STATUS -->
  <header class="glass-panel sticky top-0 z-40 transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col md:flex-row items-center justify-between gap-4">
      <div class="flex items-center space-x-3 w-full md:w-auto justify-between md:justify-start">
        <div class="flex items-center space-x-2.5">
          <div class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 pulse-dot"></span>
          </div>
          <span class="font-display font-extrabold text-xl tracking-tight text-white flex items-center gap-1.5">
            Internship<span class="text-brand">Radar</span>
            <span class="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-brand/10 text-brand border border-brand/20 tracking-normal uppercase ml-1">B.Tech CSE</span>
          </span>
        </div>
        <div class="text-xs font-mono text-slate-400 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-800">
          Sync: <span class="text-emerald-400">__GENERATED_AT__</span>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="flex items-center space-x-2 text-xs font-mono w-full md:w-auto justify-end">
        <button id="btn-export-apps" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 transition">
          <svg class="w-3.5 h-3.5 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
          Export My Tracker
        </button>
        <button id="btn-toggle-view" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 transition">
          <svg id="view-icon-grid" class="w-3.5 h-3.5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
          <span id="view-text">Compact View</span>
        </button>
      </div>
    </div>
  </header>

  <!-- HERO KPI STATS -->
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-2 w-full">
    <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
      <!-- Total -->
      <div class="glass-card rounded-xl p-4 flex flex-col justify-between border-l-4 border-l-brand">
        <div class="text-xs font-mono uppercase tracking-wider text-slate-400">Verified Tech</div>
        <div class="text-2xl font-bold font-mono text-white mt-1.5" id="stat-total">-</div>
        <div class="text-[11px] text-brand/80 mt-1 flex items-center gap-1">
          <span>● LinkedIn • Unstop • Internshala</span>
        </div>
      </div>
      <!-- High Stipend -->
      <div class="glass-card rounded-xl p-4 flex flex-col justify-between border-l-4 border-l-emerald-400">
        <div class="text-xs font-mono uppercase tracking-wider text-slate-400">High Stipend</div>
        <div class="text-2xl font-bold font-mono text-emerald-400 mt-1.5" id="stat-high-stipend">-</div>
        <div class="text-[11px] text-slate-400 mt-1">Stipend &ge; ₹20k / month</div>
      </div>
      <!-- Urgent Deadlines -->
      <div class="glass-card rounded-xl p-4 flex flex-col justify-between border-l-4 border-l-amber-400">
        <div class="text-xs font-mono uppercase tracking-wider text-slate-400">Urgent Closing</div>
        <div class="text-2xl font-bold font-mono text-amber-400 mt-1.5" id="stat-urgent">-</div>
        <div class="text-[11px] text-slate-400 mt-1">Deadline &le; __WARN_DAYS__ days</div>
      </div>
      <!-- New Today -->
      <div class="glass-card rounded-xl p-4 flex flex-col justify-between border-l-4 border-l-cyan-400">
        <div class="text-xs font-mono uppercase tracking-wider text-slate-400">New Today</div>
        <div class="text-2xl font-bold font-mono text-cyan-300 mt-1.5" id="stat-new">-</div>
        <div class="text-[11px] text-slate-400 mt-1">First spotted today</div>
      </div>
      <!-- My Tracked -->
      <div class="glass-card rounded-xl p-4 flex flex-col justify-between border-l-4 border-l-purple-400 col-span-2 sm:col-span-1">
        <div class="text-xs font-mono uppercase tracking-wider text-slate-400">My Pipeline</div>
        <div class="text-2xl font-bold font-mono text-purple-400 mt-1.5" id="stat-applied">-</div>
        <div class="text-[11px] text-slate-400 mt-1">Applied or In-Progress</div>
      </div>
    </div>
  </section>

  <!-- CONTROLS & FILTERING DOCK -->
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 w-full">
    <div class="glass-card rounded-2xl p-4 sm:p-5 flex flex-col gap-4">
      
      <!-- Search and Core Dropdowns -->
      <div class="flex flex-col md:flex-row gap-3">
        <!-- Search Bar with Hotkey -->
        <div class="relative flex-1">
          <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </div>
          <input id="f-search" type="text" placeholder="Search roles, tech stack (Python, React, AWS), companies..." class="w-full pl-10 pr-12 py-2.5 bg-slate-900/90 text-slate-100 placeholder-slate-500 rounded-xl border border-slate-700/70 focus:border-brand focus:ring-1 focus:ring-brand outline-none text-sm transition font-sans">
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <kbd class="text-[10px] font-mono text-slate-400 bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded shadow">Ctrl + /</kbd>
          </div>
        </div>

        <!-- Filter Selects -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs font-mono">
          <select id="f-source" class="bg-slate-900/90 text-slate-200 border border-slate-700/70 rounded-xl px-3 py-2.5 outline-none focus:border-brand cursor-pointer">
            <option value="">All Sources</option>
            <option value="linkedin">LinkedIn</option>
            <option value="unstop">Unstop</option>
            <option value="internshala">Internshala</option>
            <option value="watchlist">Watchlist</option>
          </select>

          <select id="f-status" class="bg-slate-900/90 text-slate-200 border border-slate-700/70 rounded-xl px-3 py-2.5 outline-none focus:border-brand cursor-pointer">
            <option value="">All Statuses</option>
            <option value="not_applied">Not Applied</option>
            <option value="applied">Applied</option>
            <option value="online_test">OA / Test</option>
            <option value="interview">Interview</option>
            <option value="offer">Offer 🎉</option>
          </select>

          <select id="f-stipend" class="bg-slate-900/90 text-slate-200 border border-slate-700/70 rounded-xl px-3 py-2.5 outline-none focus:border-brand cursor-pointer">
            <option value="0">All Stipends</option>
            <option value="10000">&ge; ₹10k /mo</option>
            <option value="20000">&ge; ₹20k /mo</option>
            <option value="30000">&ge; ₹30k /mo</option>
          </select>

          <select id="f-sort" class="bg-slate-900/90 text-slate-200 border border-slate-700/70 rounded-xl px-3 py-2.5 outline-none focus:border-brand cursor-pointer">
            <option value="match">Sort: AI Best Match</option>
            <option value="deadline">Sort: Deadline Soonest</option>
            <option value="stipend">Sort: Stipend Highest</option>
            <option value="new">Sort: Newest First</option>
          </select>
        </div>
      </div>

      <!-- Domain Category Chips -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 custom-scrollbar text-xs font-mono" id="domain-chips">
        <button class="domain-chip px-3 py-1.5 rounded-lg border border-brand bg-brand/10 text-brand font-medium whitespace-nowrap transition" data-domain="">All Domains</button>
        <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Full Stack">⚡ Full Stack</button>
        <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Backend">⚙️ Backend</button>
        <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Frontend">🎨 Frontend</button>
        <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="AI / ML">🧠 AI / ML</button>
        <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Cloud & DevOps">☁️ Cloud & DevOps</button>
        <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Mobile">📱 Mobile</button>
        <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Data Engineering">📊 Data Engineering</button>
        <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Cybersecurity">🛡️ Cybersecurity</button>
      </div>
    </div>
  </section>

  <!-- MAIN LISTINGS FEED -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 flex-1 w-full">
    <!-- Active filters indicator & count -->
    <div class="flex items-center justify-between text-xs font-mono text-slate-400 mb-4 px-1">
      <div>Showing <span id="filtered-count" class="text-brand font-bold">0</span> matching tech roles</div>
      <div id="active-filter-tags" class="flex gap-2"></div>
    </div>

    <!-- Container for Listings -->
    <div id="listings-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Injected by JavaScript -->
    </div>

    <!-- Empty state -->
    <div id="empty-state" class="hidden py-20 text-center glass-card rounded-2xl p-8 max-w-lg mx-auto">
      <div class="w-12 h-12 mx-auto rounded-full bg-slate-800 flex items-center justify-center text-slate-400 mb-3">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      </div>
      <h3 class="text-base font-semibold text-white">No matching CSE internships</h3>
      <p class="text-xs text-slate-400 mt-1">Try relaxing your search keywords or stipend filter. New positions are scraped every morning at 08:30 IST.</p>
    </div>
  </main>

  <!-- AI COLD PITCH & REFERRAL GENERATOR MODAL -->
  <div id="ai-modal" class="fixed inset-0 z-50 hidden bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="glass-card rounded-2xl max-w-2xl w-full border border-slate-700 bg-slate-900/95 overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
      <!-- Modal Header -->
      <div class="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-violet-600 flex items-center justify-center text-white font-bold text-xs shadow-md">
            AI
          </div>
          <div>
            <h3 class="font-display font-bold text-slate-100 text-base" id="modal-title">AI Cold Outreach Assistant</h3>
            <p class="text-xs text-slate-400">Tailored cold email & LinkedIn referral pitch</p>
          </div>
        </div>
        <button id="modal-close" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-5 overflow-y-auto space-y-4 custom-scrollbar text-sm">
        <div>
          <label class="block text-xs font-mono text-slate-400 mb-1">Company & Role Target</label>
          <div id="modal-target-badge" class="px-3 py-2 rounded-lg bg-slate-800/80 border border-slate-700 font-mono text-xs text-brand"></div>
        </div>

        <div>
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-mono text-slate-300 font-semibold">1. Personalized Cold Email (To Founder / Recruiter)</span>
            <button class="btn-copy text-xs font-mono text-cyan-400 hover:underline flex items-center gap-1" data-target="email-body">
              <span>Copy Email</span>
            </button>
          </div>
          <textarea id="email-body" rows="6" class="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200 outline-none focus:border-brand custom-scrollbar" readonly></textarea>
        </div>

        <div>
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-mono text-slate-300 font-semibold">2. Short LinkedIn Connection Note (Under 300 chars)</span>
            <button class="btn-copy text-xs font-mono text-violet-400 hover:underline flex items-center gap-1" data-target="linkedin-body">
              <span>Copy Note</span>
            </button>
          </div>
          <textarea id="linkedin-body" rows="3" class="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200 outline-none focus:border-brand custom-scrollbar" readonly></textarea>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="p-4 border-t border-slate-800 bg-slate-900/90 flex justify-end">
        <button id="modal-done" class="px-4 py-2 bg-brand text-slate-950 font-bold font-mono text-xs rounded-xl hover:bg-cyan-300 transition">
          Done
        </button>
      </div>
    </div>
  </div>

  <!-- TOAST NOTIFICATION -->
  <div id="toast" class="fixed bottom-5 right-5 z-50 hidden px-4 py-2.5 rounded-xl bg-slate-900 border border-brand text-brand font-mono text-xs shadow-2xl flex items-center gap-2 transition-all">
    <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
    <span id="toast-msg">Copied to clipboard!</span>
  </div>

  <!-- FOOTER -->
  <footer class="border-t border-slate-800/80 bg-slate-950/80 py-8 px-4 text-center text-xs font-mono text-slate-500">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
      <div>Internship Radar &middot; Automated daily CSE intelligence &middot; Zero fluff</div>
      <div class="flex items-center gap-4">
        <span>Bengaluru</span> &middot; <span>Hyderabad</span> &middot; <span>Pune</span> &middot; <span>Gurgaon</span> &middot; <span>Remote</span>
      </div>
    </div>
  </footer>

  <!-- EMBEDDED PREPARED DATA -->
  <script type="application/json" id="data-blob">__DATA_JSON__</script>

  <script>
    const RAW_DATA = JSON.parse(document.getElementById('data-blob').textContent);
    const WARN_DAYS = __WARN_DAYS__;

    // LocalStorage key for tracking applications directly in browser
    const LOCAL_APPS_KEY = "internship_tracker_user_apps";
    let userApplications = {};
    try {
      const stored = localStorage.getItem(LOCAL_APPS_KEY);
      if (stored) userApplications = JSON.parse(stored);
    } catch(e) {
      console.warn("Could not read local storage:", e);
    }

    // Merge localStorage status with RAW_DATA
    RAW_DATA.forEach(item => {
      if (userApplications[item.id]) {
        item.status = userApplications[item.id].status || item.status;
        item.status_label = userApplications[item.id].status_label || item.status_label;
      }
    });

    let currentDomain = "";
    let isCompactView = false;

    // Days calculation helper
    function daysUntil(dateStr) {
      if (!dateStr) return null;
      const parsed = Date.parse(dateStr);
      if (isNaN(parsed)) return null;
      const diff = (parsed - Date.now()) / (1000 * 60 * 60 * 24);
      return Math.ceil(diff);
    }

    // Toast helper
    function showToast(msg) {
      const toast = document.getElementById('toast');
      document.getElementById('toast-msg').textContent = msg;
      toast.classList.remove('hidden');
      setTimeout(() => toast.classList.add('hidden'), 2400);
    }

    // Source styling
    function getSourceBadge(source) {
      const s = (source || '').toLowerCase();
      if (s === 'linkedin') {
        return '<span class="px-2 py-0.5 rounded-md bg-[#0A66C2]/15 text-[#38BDF8] border border-[#0A66C2]/30 font-mono text-[10px] font-semibold">LinkedIn</span>';
      } else if (s === 'unstop') {
        return '<span class="px-2 py-0.5 rounded-md bg-[#00D2A0]/15 text-[#34D399] border border-[#00D2A0]/30 font-mono text-[10px] font-semibold">Unstop</span>';
      } else if (s === 'internshala') {
        return '<span class="px-2 py-0.5 rounded-md bg-[#008BDC]/15 text-[#38BDF8] border border-[#008BDC]/30 font-mono text-[10px] font-semibold">Internshala</span>';
      }
      return '<span class="px-2 py-0.5 rounded-md bg-purple-500/15 text-purple-300 border border-purple-500/30 font-mono text-[10px] font-semibold">Watchlist</span>';
    }

    // Status styling
    function getStatusBadge(status) {
      const map = {
        'not_applied': 'bg-slate-800 text-slate-400 border-slate-700',
        'applied': 'bg-blue-900/40 text-blue-300 border-blue-700',
        'online_test': 'bg-purple-900/40 text-purple-300 border-purple-700',
        'interview': 'bg-amber-900/40 text-amber-300 border-amber-700',
        'offer': 'bg-emerald-900/40 text-emerald-300 border-emerald-500',
        'rejected': 'bg-rose-900/40 text-rose-300 border-rose-800',
      };
      const cls = map[status] || map['not_applied'];
      const label = (status || 'not_applied').replace('_', ' ').toUpperCase();
      return `<span class="px-2 py-0.5 rounded text-[10px] font-mono border ${cls}">${label}</span>`;
    }

    // Render cards or compact table
    function render() {
      const search = document.getElementById('f-search').value.toLowerCase().trim();
      const source = document.getElementById('f-source').value;
      const status = document.getElementById('f-status').value;
      const minStipend = parseInt(document.getElementById('f-stipend').value) || 0;
      const sortBy = document.getElementById('f-sort').value;

      let items = RAW_DATA.filter(item => {
        if (source && item.source !== source) return false;
        if (status && item.status !== status) return false;
        if (currentDomain && item.domain !== currentDomain) return false;
        if (minStipend > 0 && (item.stipend_amount || 0) < minStipend) return false;
        if (search) {
          const matchStr = `${item.title} ${item.company} ${item.location} ${(item.tags || []).join(' ')} ${item.description || ''}`.toLowerCase();
          if (!matchStr.includes(search)) return false;
        }
        return true;
      });

      // Sorting
      if (sortBy === 'deadline') {
        items.sort((a, b) => {
          const da = daysUntil(a.apply_by_iso), db = daysUntil(b.apply_by_iso);
          if (da === null) return 1;
          if (db === null) return -1;
          return da - db;
        });
      } else if (sortBy === 'stipend') {
        items.sort((a, b) => (b.stipend_amount || 0) - (a.stipend_amount || 0));
      } else if (sortBy === 'new') {
        items.sort((a, b) => (b.first_seen_at || '').localeCompare(a.first_seen_at || ''));
      } else {
        // AI best match (score)
        items.sort((a, b) => (b.cse_score || 0) - (a.cse_score || 0));
      }

      document.getElementById('filtered-count').textContent = items.length;
      const container = document.getElementById('listings-container');
      const emptyState = document.getElementById('empty-state');

      if (items.length === 0) {
        container.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
      }
      emptyState.classList.add('hidden');

      if (isCompactView) {
        // Table view
        container.className = "w-full overflow-x-auto glass-card rounded-2xl p-2";
        let html = `
          <table class="w-full text-left text-xs font-mono">
            <thead class="text-slate-400 border-b border-slate-800 text-[11px] uppercase">
              <tr>
                <th class="p-3">Role & Company</th>
                <th class="p-3">Domain</th>
                <th class="p-3">Stipend</th>
                <th class="p-3">Deadline</th>
                <th class="p-3">Source</th>
                <th class="p-3">Status</th>
                <th class="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
        `;
        items.forEach(item => {
          const days = daysUntil(item.apply_by_iso);
          let deadlineBadge = `<span class="text-slate-400">${item.apply_by || 'Rolling'}</span>`;
          if (days !== null) {
            if (days < 0) deadlineBadge = `<span class="text-rose-400 font-bold">Expired</span>`;
            else if (days <= WARN_DAYS) deadlineBadge = `<span class="text-amber-400 font-bold">⏳ ${days}d left</span>`;
          }
          html += `
            <tr class="hover:bg-slate-800/40 transition">
              <td class="p-3">
                <a href="${item.link}" target="_blank" rel="noopener" class="font-sans font-semibold text-white hover:text-brand transition text-sm flex items-center gap-1.5">
                  ${item.title}
                  <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                </a>
                <div class="text-slate-400 text-xs mt-0.5">${item.company} &middot; <span class="text-slate-500">${item.location}</span></div>
              </td>
              <td class="p-3"><span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px]">${item.domain || 'Tech'}</span></td>
              <td class="p-3 text-emerald-400 font-semibold">${item.stipend_text}</td>
              <td class="p-3">${deadlineBadge}</td>
              <td class="p-3">${getSourceBadge(item.source)}</td>
              <td class="p-3">
                <select class="status-select bg-slate-900 border border-slate-700 text-slate-300 rounded px-1.5 py-1 text-[10px]" data-id="${item.id}">
                  <option value="not_applied" ${item.status==='not_applied'?'selected':''}>Not Applied</option>
                  <option value="applied" ${item.status==='applied'?'selected':''}>Applied</option>
                  <option value="online_test" ${item.status==='online_test'?'selected':''}>OA / Test</option>
                  <option value="interview" ${item.status==='interview'?'selected':''}>Interview</option>
                  <option value="offer" ${item.status==='offer'?'selected':''}>Offer 🎉</option>
                </select>
              </td>
              <td class="p-3 text-right">
                <button class="btn-ai px-2.5 py-1 bg-violet-600/20 hover:bg-violet-600/40 text-violet-300 border border-violet-500/30 rounded text-[10px] transition" data-id="${item.id}">
                  AI Pitch
                </button>
              </td>
            </tr>
          `;
        });
        html += `</tbody></table>`;
        container.innerHTML = html;
      } else {
        // Grid cards view
        container.className = "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4";
        container.innerHTML = items.map(item => {
          const days = daysUntil(item.apply_by_iso);
          let deadlineBadge = `<span class="text-slate-400 font-mono text-[11px]">${item.apply_by || 'Rolling'}</span>`;
          if (days !== null) {
            if (days < 0) deadlineBadge = `<span class="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-mono text-[10px]">Closed</span>`;
            else if (days <= WARN_DAYS) deadlineBadge = `<span class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 font-mono text-[10px] animate-pulse">🔥 ${days} days left</span>`;
          }

          const tagsHtml = (item.tags || []).slice(0, 4).map(t => 
            `<span class="px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700/60 font-mono text-[10px]">${t}</span>`
          ).join('');

          const isNew = item.is_new_today ? `<span class="px-1.5 py-0.5 rounded bg-brand/20 text-brand border border-brand/40 text-[9px] font-mono font-bold tracking-wider uppercase">NEW</span>` : '';

          return `
            <div class="glass-card rounded-2xl p-4 flex flex-col justify-between transition-all group relative">
              <div>
                <!-- Top metadata row -->
                <div class="flex items-center justify-between gap-2 mb-2">
                  <div class="flex items-center gap-1.5 flex-wrap">
                    ${getSourceBadge(item.source)}
                    <span class="px-2 py-0.5 rounded-md bg-slate-800/70 text-slate-300 border border-slate-700/50 font-mono text-[10px]">${item.domain || 'Tech'}</span>
                    ${isNew}
                  </div>
                  <div>${deadlineBadge}</div>
                </div>

                <!-- Title & Company -->
                <a href="${item.link}" target="_blank" rel="noopener" class="font-sans font-bold text-white text-base hover:text-brand transition flex items-start justify-between gap-2 group-hover:translate-x-0.5">
                  <span>${item.title}</span>
                  <svg class="w-4 h-4 text-slate-500 shrink-0 mt-1 opacity-70 group-hover:opacity-100 group-hover:text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                </a>
                <div class="text-xs text-slate-400 mt-1 flex items-center gap-2">
                  <span class="font-medium text-slate-200">${item.company}</span>
                  <span>&middot;</span>
                  <span class="truncate text-slate-400">${item.location}</span>
                </div>

                <!-- Stipend Badge -->
                <div class="mt-3.5 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-xs font-semibold">
                  <span>💰</span>
                  <span>${item.stipend_text}</span>
                </div>

                <!-- Tech Tags -->
                <div class="mt-3 flex flex-wrap gap-1.5">
                  ${tagsHtml}
                </div>
              </div>

              <!-- Action Bar -->
              <div class="mt-4 pt-3.5 border-t border-slate-800/80 flex items-center justify-between gap-2">
                <!-- Status updater -->
                <div class="flex items-center gap-1">
                  <select class="status-select bg-slate-900 border border-slate-700 hover:border-slate-500 text-slate-300 rounded-lg px-2 py-1 font-mono text-[11px] outline-none cursor-pointer" data-id="${item.id}">
                    <option value="not_applied" ${item.status==='not_applied'?'selected':''}>⚪ Not Applied</option>
                    <option value="applied" ${item.status==='applied'?'selected':''}>🔵 Applied</option>
                    <option value="online_test" ${item.status==='online_test'?'selected':''}>🟣 OA / Test</option>
                    <option value="interview" ${item.status==='interview'?'selected':''}>🟠 Interview</option>
                    <option value="offer" ${item.status==='offer'?'selected':''}>🟢 Offer 🎉</option>
                  </select>
                </div>

                <!-- AI Cold Pitch -->
                <button class="btn-ai px-3 py-1.5 bg-gradient-to-r from-violet-600/20 to-cyan-600/20 hover:from-violet-600/40 hover:to-cyan-600/40 text-cyan-300 border border-cyan-500/30 rounded-lg font-mono text-xs flex items-center gap-1.5 transition active:scale-95 shadow-sm" data-id="${item.id}">
                  <span>✨ AI Pitch</span>
                </button>
              </div>
            </div>
          `;
        }).join('');
      }

      attachInteractiveListeners();
    }

    // Attach listener for dynamic items
    function attachInteractiveListeners() {
      // Status selector change
      document.querySelectorAll('.status-select').forEach(sel => {
        sel.addEventListener('change', (e) => {
          const id = e.target.dataset.id;
          const newStatus = e.target.value;
          const item = RAW_DATA.find(d => d.id === id);
          if (item) {
            item.status = newStatus;
            item.status_label = newStatus.replace('_', ' ').toUpperCase();
            userApplications[id] = {
              status: newStatus,
              status_label: item.status_label,
              title: item.title,
              company: item.company,
              updated_at: new Date().toISOString()
            };
            try {
              localStorage.setItem(LOCAL_APPS_KEY, JSON.stringify(userApplications));
            } catch(err) {
              console.error(err);
            }
            updateCounters();
            showToast(`Status updated: ${newStatus.toUpperCase()}`);
          }
        });
      });

      // AI Pitch Button
      document.querySelectorAll('.btn-ai').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.dataset.id;
          const item = RAW_DATA.find(d => d.id === id);
          if (item) openAiModal(item);
        });
      });
    }

    // Open AI Generator Modal
    function openAiModal(item) {
      const skills = (item.tags || ['Python', 'Data Structures', 'Git']).join(', ');
      document.getElementById('modal-target-badge').textContent = `${item.title} @ ${item.company} [${item.domain || 'Tech'}]`;

      const emailText = 
`Subject: Application: ${item.title} - B.Tech CSE Candidate

Hi Team,

I am writing to express my strong interest in the ${item.title} role at ${item.company}. 

As a Computer Science & Engineering student with hands-on experience in ${skills}, I have built production-ready applications, optimized backend APIs, and actively solve algorithmic challenges.

I am eager to contribute immediately to ${item.company}'s engineering initiatives. You can explore my technical projects and code on GitHub.

Could we schedule a brief 10-minute introductory call this week?

Warm regards,
Raghav Bajaj
B.Tech Computer Science & Engineering`;

      const linkedinText = 
`Hi! I saw the ${item.title} opening at ${item.company}. As a B.Tech CSE student passionate about ${skills}, I'd love to connect and learn more about engineering at ${item.company}. Would you be open to sharing a quick tip or referral? Thanks!`;

      document.getElementById('email-body').value = emailText;
      document.getElementById('linkedin-body').value = linkedinText;
      document.getElementById('ai-modal').classList.remove('hidden');
    }

    // Modal controls
    document.getElementById('modal-close').addEventListener('click', () => {
      document.getElementById('ai-modal').classList.add('hidden');
    });
    document.getElementById('modal-done').addEventListener('click', () => {
      document.getElementById('ai-modal').classList.add('hidden');
    });

    // Copy handlers
    document.querySelectorAll('.btn-copy').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.dataset.target;
        const text = document.getElementById(targetId).value;
        navigator.clipboard.writeText(text).then(() => {
          showToast('Copied to clipboard!');
        });
      });
    });

    // Domain chips
    document.querySelectorAll('.domain-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('.domain-chip').forEach(c => {
          c.classList.remove('border-brand', 'bg-brand/10', 'text-brand', 'font-medium');
          c.classList.add('border-slate-800', 'bg-slate-900/80', 'text-slate-300');
        });
        chip.classList.add('border-brand', 'bg-brand/10', 'text-brand', 'font-medium');
        chip.classList.remove('border-slate-800', 'bg-slate-900/80', 'text-slate-300');
        currentDomain = chip.dataset.domain;
        render();
      });
    });

    // View toggle
    document.getElementById('btn-toggle-view').addEventListener('click', () => {
      isCompactView = !isCompactView;
      document.getElementById('view-text').textContent = isCompactView ? 'Card Grid' : 'Compact View';
      render();
    });

    // Export Applications JSON
    document.getElementById('btn-export-apps').addEventListener('click', () => {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(userApplications, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", "applications.json");
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
      showToast('Exported applications.json!');
    });

    // Search hotkey
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        document.getElementById('f-search').focus();
      }
    });

    // Filter change listeners
    document.getElementById('f-search').addEventListener('input', render);
    document.getElementById('f-source').addEventListener('change', render);
    document.getElementById('f-status').addEventListener('change', render);
    document.getElementById('f-stipend').addEventListener('change', render);
    document.getElementById('f-sort').addEventListener('change', render);

    // Update KPI Counters
    function updateCounters() {
      document.getElementById('stat-total').textContent = RAW_DATA.length;
      document.getElementById('stat-new').textContent = RAW_DATA.filter(d => d.is_new_today).length;
      document.getElementById('stat-high-stipend').textContent = RAW_DATA.filter(d => (d.stipend_amount || 0) >= 20000).length;
      document.getElementById('stat-urgent').textContent = RAW_DATA.filter(d => {
        const days = daysUntil(d.apply_by_iso);
        return days !== null && days >= 0 && days <= WARN_DAYS;
      }).length;
      document.getElementById('stat-applied').textContent = RAW_DATA.filter(d => d.status && d.status !== 'not_applied').length;
    }

    updateCounters();
    render();
  </script>
</body>
</html>
"""


def build():
    internships = load_internships()
    applications = load_applications()
    today = date.today().isoformat()

    items = []
    for iid, rec in internships.items():
        # Check if expired more than grace days
        apply_iso = _parse_deadline_to_iso(rec.get("apply_by", ""))
        
        app = applications.get(iid, {})
        status = app.get("status", "not_applied")
        first_seen = (rec.get("first_seen_at") or "")[:10]

        items.append({
            "id": iid,
            "title": rec.get("title", "Untitled Software Intern"),
            "company": rec.get("company", "Unknown"),
            "location": rec.get("location", "Not specified"),
            "stipend_text": rec.get("stipend_text", "Competitive"),
            "stipend_amount": rec.get("stipend_amount", 0),
            "apply_by": rec.get("apply_by", "Rolling"),
            "apply_by_iso": apply_iso,
            "link": rec.get("link", "#"),
            "source": rec.get("source", "internshala"),
            "status": status,
            "status_label": STATUS_LABELS.get(status, status),
            "domain": rec.get("domain", "Core Software Dev"),
            "tags": rec.get("tags", []),
            "cse_score": rec.get("cse_score", 75),
            "description": (rec.get("description") or "")[:250],
            "first_seen_at": rec.get("first_seen_at", ""),
            "is_new_today": first_seen == today,
        })

    os.makedirs(DOCS_DIR, exist_ok=True)
    html = DASHBOARD_TEMPLATE.replace("__DATA_JSON__", json.dumps(items, ensure_ascii=False))
    html = html.replace("__GENERATED_AT__", datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC"))
    html = html.replace("__WARN_DAYS__", str(DEADLINE_WARNING_DAYS))

    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Refreshed high-performance dashboard written to {out_path} ({len(items)} CSE listings)")


if __name__ == "__main__":
    build()
