"""
Generates the modern, high-performance static dashboard in docs/index.html.
Engineered with an ultra-sleek dual dark-theme system (Cyber Obsidian ⇋ Synthwave Sunset),
accurate deadline & expiration engine, IST synchronization time, and AI cold outreach assistant.
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


def _parse_deadline_to_iso(apply_by_text: str):
    """
    Parses natural free text deadline into ISO YYYY-MM-DD.
    Never pushes past dates to the next year.
    """
    if not apply_by_text or apply_by_text.strip().lower() in ("unknown", "not specified", "open", "rolling", "asap", ""):
        return None
    cleaned = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", apply_by_text, flags=re.IGNORECASE)
    cleaned = re.sub(r"'\s*(\d{2})\b", r" 20\1", cleaned)
    try:
        parsed = dateutil_parser.parse(cleaned, fuzzy=True, default=datetime(date.today().year, 1, 1))
        return parsed.date().isoformat()
    except (ValueError, OverflowError):
        return None


DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="cyber" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Internship Radar | B.Tech CSE Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
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
            synth: ['Space Grotesk', 'sans-serif'],
          }
        }
      }
    }
  </script>
  <style>
    /* THEME 1: CYBER OBSIDIAN (DEFAULT) */
    :root, [data-theme="cyber"] {
      --bg-base: #070A0F;
      --bg-surface: #0D131F;
      --bg-card: rgba(18, 26, 43, 0.78);
      --bg-hover: #162035;
      --border-color: rgba(255, 255, 255, 0.08);
      --border-glow: rgba(0, 240, 255, 0.35);
      --accent-primary: #00F0FF;
      --accent-primary-hover: #38BDF8;
      --accent-glow: rgba(0, 240, 255, 0.12);
      --accent-secondary: #8B5CF6;
      --radar-dot: #10B981;
      --radar-ping: rgba(16, 185, 129, 0.7);
      --card-shadow: rgba(0, 240, 255, 0.05);
      --theme-name: "Cyber Obsidian";
      --theme-indicator: #00F0FF;
      --header-bg: rgba(13, 19, 31, 0.88);
      --body-gradient: 
        radial-gradient(at 0% 0%, rgba(6, 182, 212, 0.08) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.08) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
    }

    /* THEME 2: SYNTHWAVE SUNSET (COMPLETELY DIFFERENT RETRO-CYBER DARK THEME) */
    [data-theme="synthwave"] {
      --bg-base: #0B0716;
      --bg-surface: #140D26;
      --bg-card: rgba(27, 18, 48, 0.82);
      --bg-hover: #261A42;
      --border-color: rgba(255, 46, 147, 0.18);
      --border-glow: rgba(255, 46, 147, 0.5);
      --accent-primary: #FF2E93;
      --accent-primary-hover: #F43F5E;
      --accent-glow: rgba(255, 46, 147, 0.2);
      --accent-secondary: #FF8A00;
      --radar-dot: #FF2E93;
      --radar-ping: rgba(255, 46, 147, 0.8);
      --card-shadow: rgba(255, 46, 147, 0.08);
      --theme-name: "Synthwave Sunset";
      --theme-indicator: #FF2E93;
      --header-bg: rgba(20, 13, 38, 0.9);
      --body-gradient: 
        radial-gradient(at 0% 0%, rgba(255, 46, 147, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(255, 138, 0, 0.12) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(139, 92, 246, 0.08) 0px, transparent 50%);
    }

    body {
      background-color: var(--bg-base);
      background-image: var(--body-gradient);
      background-attachment: fixed;
      color: #F1F5F9;
      transition: background-color 0.3s ease, background-image 0.3s ease;
    }

    .custom-scrollbar::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
      background: var(--bg-surface);
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background: #2D3748;
      border-radius: 3px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
      background: #4A5568;
    }

    .glass-card {
      background: var(--bg-card);
      backdrop-filter: blur(14px);
      border: 1px solid var(--border-color);
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
      border-color: var(--border-glow);
      box-shadow: 0 10px 30px var(--card-shadow);
    }
    .glass-panel {
      background: var(--header-bg);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-color);
    }

    .pulse-dot {
      background-color: var(--radar-dot);
      box-shadow: 0 0 0 0 var(--radar-ping);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 var(--radar-ping); }
      70% { box-shadow: 0 0 0 8px rgba(0, 0, 0, 0); }
      100% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); }
    }

    .theme-accent-text {
      color: var(--accent-primary);
    }
    .theme-accent-bg {
      background-color: var(--accent-primary);
    }
    .theme-border {
      border-color: var(--border-color);
    }
  </style>
</head>
<body class="min-h-screen flex flex-col font-sans selection:bg-cyan-500 selection:text-black custom-scrollbar">

  <!-- TOP BAR & STATUS -->
  <header class="glass-panel sticky top-0 z-40 transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col md:flex-row items-center justify-between gap-4">
      <div class="flex items-center space-x-3 w-full md:w-auto justify-between md:justify-start">
        <div class="flex items-center space-x-2.5">
          <div class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 pulse-dot"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 pulse-dot"></span>
          </div>
          <span class="font-display font-extrabold text-xl tracking-tight text-white flex items-center gap-1.5">
            Internship<span class="theme-accent-text">Radar</span>
            <span class="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 tracking-normal uppercase ml-1">B.Tech CSE</span>
          </span>
        </div>
        
        <!-- IST Time Badge -->
        <div class="text-xs font-mono text-slate-300 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800 flex items-center gap-2">
          <span class="text-slate-400">Sync:</span>
          <span class="text-emerald-400 font-bold" id="sync-timestamp">__GENERATED_AT__</span>
        </div>
      </div>

      <!-- Quick Actions & Theme Switcher -->
      <div class="flex items-center space-x-2.5 text-xs font-mono w-full md:w-auto justify-end flex-wrap">
        <!-- Theme Switcher Button -->
        <button id="btn-theme-toggle" class="px-3 py-1.5 rounded-lg bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700/80 flex items-center gap-2 transition active:scale-95 shadow-sm" title="Toggle between Cyber Obsidian and Synthwave Sunset themes">
          <span class="w-2.5 h-2.5 rounded-full inline-block" style="background-color: var(--accent-primary);"></span>
          <span id="theme-display-name">Cyber Obsidian</span>
          <span class="text-[10px] text-slate-400">⇄</span>
        </button>

        <button id="btn-export-apps" class="px-3 py-1.5 rounded-lg bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700/80 flex items-center gap-1.5 transition">
          <svg class="w-3.5 h-3.5 theme-accent-text" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
          Export Tracker
        </button>

        <button id="btn-toggle-view" class="px-3 py-1.5 rounded-lg bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700/80 flex items-center gap-1.5 transition">
          <svg class="w-3.5 h-3.5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
          <span id="view-text">Compact View</span>
        </button>
      </div>
    </div>
  </header>

  <!-- KPI METRICS -->
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-2 w-full">
    <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
      <!-- Active Open -->
      <div class="glass-card rounded-xl p-4 flex flex-col justify-between border-l-4 border-l-cyan-400">
        <div class="text-xs font-mono uppercase tracking-wider text-slate-400">Open & Active</div>
        <div class="text-2xl font-bold font-mono text-cyan-300 mt-1.5" id="stat-active">-</div>
        <div class="text-[11px] text-slate-400 mt-1">Verified non-expired CSE</div>
      </div>
      <!-- High Stipend -->
      <div class="glass-card rounded-xl p-4 flex flex-col justify-between border-l-4 border-l-emerald-400">
        <div class="text-xs font-mono uppercase tracking-wider text-slate-400">High Stipend</div>
        <div class="text-2xl font-bold font-mono text-emerald-400 mt-1.5" id="stat-high-stipend">-</div>
        <div class="text-[11px] text-slate-400 mt-1">Stipend &ge; ₹20k / month</div>
      </div>
      <!-- Urgent Deadlines -->
      <div class="glass-card rounded-xl p-4 flex flex-col justify-between border-l-4 border-l-amber-400">
        <div class="text-xs font-mono uppercase tracking-wider text-slate-400">Closing Soon</div>
        <div class="text-2xl font-bold font-mono text-amber-400 mt-1.5" id="stat-urgent">-</div>
        <div class="text-[11px] text-slate-400 mt-1">Deadline &le; __WARN_DAYS__ days</div>
      </div>
      <!-- Closed / Past -->
      <div class="glass-card rounded-xl p-4 flex flex-col justify-between border-l-4 border-l-rose-500">
        <div class="text-xs font-mono uppercase tracking-wider text-slate-400">Past Deadline</div>
        <div class="text-2xl font-bold font-mono text-rose-400 mt-1.5" id="stat-expired">-</div>
        <div class="text-[11px] text-slate-400 mt-1">Closed or Stale</div>
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
          <input id="f-search" type="text" placeholder="Search roles, tech skills (Python, React, AWS), companies..." class="w-full pl-10 pr-12 py-2.5 bg-slate-950/80 text-slate-100 placeholder-slate-500 rounded-xl border border-slate-700/70 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none text-sm transition font-sans">
          <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <kbd class="text-[10px] font-mono text-slate-400 bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded shadow">Ctrl + /</kbd>
          </div>
        </div>

        <!-- Filter Selects -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs font-mono">
          <select id="f-source" class="bg-slate-950/80 text-slate-200 border border-slate-700/70 rounded-xl px-3 py-2.5 outline-none focus:border-cyan-400 cursor-pointer">
            <option value="">All Sources</option>
            <option value="linkedin">LinkedIn</option>
            <option value="unstop">Unstop</option>
            <option value="internshala">Internshala</option>
            <option value="watchlist">Watchlist</option>
          </select>

          <select id="f-status" class="bg-slate-950/80 text-slate-200 border border-slate-700/70 rounded-xl px-3 py-2.5 outline-none focus:border-cyan-400 cursor-pointer">
            <option value="">All Statuses</option>
            <option value="not_applied">Not Applied</option>
            <option value="applied">Applied</option>
            <option value="online_test">OA / Test</option>
            <option value="interview">Interview</option>
            <option value="offer">Offer 🎉</option>
          </select>

          <select id="f-stipend" class="bg-slate-950/80 text-slate-200 border border-slate-700/70 rounded-xl px-3 py-2.5 outline-none focus:border-cyan-400 cursor-pointer">
            <option value="0">All Stipends</option>
            <option value="10000">&ge; ₹10k /mo</option>
            <option value="20000">&ge; ₹20k /mo</option>
            <option value="30000">&ge; ₹30k /mo</option>
          </select>

          <select id="f-sort" class="bg-slate-950/80 text-slate-200 border border-slate-700/70 rounded-xl px-3 py-2.5 outline-none focus:border-cyan-400 cursor-pointer">
            <option value="match">Sort: AI Best Match</option>
            <option value="deadline">Sort: Deadline Soonest</option>
            <option value="stipend">Sort: Stipend Highest</option>
            <option value="new">Sort: Newest First</option>
          </select>
        </div>
      </div>

      <!-- Quick Action Toggles & Domain Chips -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1 border-t border-slate-800/60">
        <!-- Domain Category Chips -->
        <div class="flex items-center gap-1.5 overflow-x-auto pb-1 max-w-full custom-scrollbar text-xs font-mono" id="domain-chips">
          <button class="domain-chip px-3 py-1.5 rounded-lg border border-cyan-400 bg-cyan-500/10 text-cyan-300 font-medium whitespace-nowrap transition" data-domain="">All Domains</button>
          <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Full Stack">⚡ Full Stack</button>
          <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Backend">⚙️ Backend</button>
          <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Frontend">🎨 Frontend</button>
          <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="AI / ML">🧠 AI / ML</button>
          <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Cloud & DevOps">☁️ Cloud & DevOps</button>
          <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Mobile">📱 Mobile</button>
          <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Data Engineering">📊 Data Engineering</button>
          <button class="domain-chip px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 text-slate-300 hover:border-slate-600 whitespace-nowrap transition" data-domain="Cybersecurity">🛡️ Cybersecurity</button>
        </div>

        <!-- Hide Expired Toggle Checkbox -->
        <label class="flex items-center gap-2 cursor-pointer text-xs font-mono select-none px-2.5 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-slate-700 whitespace-nowrap shrink-0">
          <input type="checkbox" id="toggle-hide-expired" class="w-4 h-4 rounded text-cyan-500 focus:ring-0 bg-slate-950 border-slate-700 cursor-pointer" checked>
          <span class="text-slate-300">Active Roles Only</span>
          <span class="text-[10px] text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/40" id="badge-active-count">0</span>
        </label>
      </div>

    </div>
  </section>

  <!-- MAIN LISTINGS FEED -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 flex-1 w-full">
    <!-- Active filters indicator & count -->
    <div class="flex items-center justify-between text-xs font-mono text-slate-400 mb-4 px-1">
      <div>Showing <span id="filtered-count" class="theme-accent-text font-bold">0</span> opportunities</div>
      <div id="filter-hint" class="text-[11px] text-slate-500 hidden sm:block">Expired deadlines are clearly labeled and hidden by default</div>
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
      <p class="text-xs text-slate-400 mt-1">Try relaxing your filters or unchecking "Active Roles Only". New tech roles are scraped every morning at 08:30 IST.</p>
    </div>
  </main>

  <!-- AI COLD PITCH & REFERRAL GENERATOR MODAL -->
  <div id="ai-modal" class="fixed inset-0 z-50 hidden bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
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
          <label class="block text-xs font-mono text-slate-400 mb-1">Target Role & Company</label>
          <div id="modal-target-badge" class="px-3 py-2 rounded-lg bg-slate-800/80 border border-slate-700 font-mono text-xs theme-accent-text"></div>
        </div>

        <div>
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-mono text-slate-300 font-semibold">1. Personalized Cold Email (To Founder / Recruiter)</span>
            <button class="btn-copy text-xs font-mono text-cyan-400 hover:underline flex items-center gap-1" data-target="email-body">
              <span>Copy Email</span>
            </button>
          </div>
          <textarea id="email-body" rows="6" class="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200 outline-none focus:border-cyan-400 custom-scrollbar" readonly></textarea>
        </div>

        <div>
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-mono text-slate-300 font-semibold">2. Short LinkedIn Connection Note (&le; 300 chars)</span>
            <button class="btn-copy text-xs font-mono text-violet-400 hover:underline flex items-center gap-1" data-target="linkedin-body">
              <span>Copy Note</span>
            </button>
          </div>
          <textarea id="linkedin-body" rows="3" class="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200 outline-none focus:border-cyan-400 custom-scrollbar" readonly></textarea>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="p-4 border-t border-slate-800 bg-slate-900/90 flex justify-end">
        <button id="modal-done" class="px-4 py-2 bg-cyan-400 text-slate-950 font-bold font-mono text-xs rounded-xl hover:bg-cyan-300 transition">
          Done
        </button>
      </div>
    </div>
  </div>

  <!-- TOAST NOTIFICATION -->
  <div id="toast" class="fixed bottom-5 right-5 z-50 hidden px-4 py-2.5 rounded-xl bg-slate-900 border border-cyan-400 text-cyan-300 font-mono text-xs shadow-2xl flex items-center gap-2 transition-all">
    <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
    <span id="toast-msg">Copied to clipboard!</span>
  </div>

  <!-- FOOTER -->
  <footer class="border-t border-slate-800/80 bg-slate-950/90 py-8 px-4 text-center text-xs font-mono text-slate-500">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
      <div>Internship Radar &middot; Automated B.Tech CSE Intelligence &middot; IST Synchronized</div>
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

    // THEME SYSTEM (CYBER OBSIDIAN ⇋ SYNTHWAVE SUNSET)
    const THEMES = {
      cyber: {
        name: "Cyber Obsidian",
        color: "#00F0FF",
        next: "synthwave"
      },
      synthwave: {
        name: "Synthwave Sunset",
        color: "#FF2E93",
        next: "cyber"
      }
    };

    let currentTheme = localStorage.getItem("radar_theme") || "cyber";
    function applyTheme(themeKey) {
      if (!THEMES[themeKey]) themeKey = "cyber";
      currentTheme = themeKey;
      document.documentElement.setAttribute("data-theme", themeKey);
      localStorage.setItem("radar_theme", themeKey);
      document.getElementById("theme-display-name").textContent = THEMES[themeKey].name;
    }
    applyTheme(currentTheme);

    document.getElementById("btn-theme-toggle").addEventListener("click", () => {
      const nextTheme = THEMES[currentTheme].next;
      applyTheme(nextTheme);
      showToast(`Switched theme to ${THEMES[nextTheme].name}`);
    });

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

    // Days calculation helper (using local date comparison for precision)
    function daysUntil(dateStr) {
      if (!dateStr) return null;
      const targetDate = new Date(dateStr + "T23:59:59");
      if (isNaN(targetDate.getTime())) return null;
      const now = new Date();
      const diffTime = targetDate - now;
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    // Toast helper
    function showToast(msg) {
      const toast = document.getElementById('toast');
      document.getElementById('toast-msg').textContent = msg;
      toast.classList.remove('hidden');
      setTimeout(() => toast.classList.add('hidden'), 2400);
    }

    // Source badge generator
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

    // Main render function
    function render() {
      const search = document.getElementById('f-search').value.toLowerCase().trim();
      const source = document.getElementById('f-source').value;
      const status = document.getElementById('f-status').value;
      const minStipend = parseInt(document.getElementById('f-stipend').value) || 0;
      const sortBy = document.getElementById('f-sort').value;
      const hideExpired = document.getElementById('toggle-hide-expired').checked;

      let items = RAW_DATA.filter(item => {
        if (hideExpired && item.is_expired) return false;
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
          if (a.is_expired && !b.is_expired) return 1;
          if (!a.is_expired && b.is_expired) return -1;
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
        // Compact Table View
        container.className = "w-full overflow-x-auto glass-card rounded-2xl p-2";
        let html = `
          <table class="w-full text-left text-xs font-mono">
            <thead class="text-slate-400 border-b border-slate-800 text-[11px] uppercase">
              <tr>
                <th class="p-3">Role & Company</th>
                <th class="p-3">Domain</th>
                <th class="p-3">Stipend</th>
                <th class="p-3">Deadline Status</th>
                <th class="p-3">Source</th>
                <th class="p-3">Status</th>
                <th class="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
        `;
        items.forEach(item => {
          const days = daysUntil(item.apply_by_iso);
          let deadlineBadge = '';
          if (item.is_expired || (days !== null && days < 0)) {
            deadlineBadge = `<span class="px-2 py-0.5 rounded bg-rose-500/15 text-rose-400 border border-rose-500/30 font-mono text-[10px] font-semibold">🛑 Closed (${item.apply_by || 'Expired'})</span>`;
          } else if (days !== null && days <= WARN_DAYS) {
            deadlineBadge = `<span class="px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30 font-mono text-[10px] font-semibold animate-pulse">🔥 ${days === 0 ? 'Closes Today' : days + 'd left'} (${item.apply_by})</span>`;
          } else if (days !== null) {
            deadlineBadge = `<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60 font-mono text-[10px]">${item.apply_by}</span>`;
          } else {
            deadlineBadge = `<span class="px-2 py-0.5 rounded bg-cyan-950/40 text-cyan-300 border border-cyan-800/40 font-mono text-[10px]">Rolling / Open</span>`;
          }

          html += `
            <tr class="hover:bg-slate-800/40 transition">
              <td class="p-3">
                <a href="${item.link}" target="_blank" rel="noopener" class="font-sans font-semibold text-white hover:text-cyan-400 transition text-sm flex items-center gap-1.5">
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
        // Visual Card Grid View
        container.className = "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4";
        container.innerHTML = items.map(item => {
          const days = daysUntil(item.apply_by_iso);
          let deadlineBadge = '';
          if (item.is_expired || (days !== null && days < 0)) {
            deadlineBadge = `<span class="px-2 py-0.5 rounded bg-rose-500/15 text-rose-400 border border-rose-500/30 font-mono text-[10px] font-semibold flex items-center gap-1">🛑 Closed (${item.apply_by || 'Expired'})</span>`;
          } else if (days !== null && days <= WARN_DAYS) {
            deadlineBadge = `<span class="px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30 font-mono text-[10px] font-semibold flex items-center gap-1 animate-pulse">🔥 ${days === 0 ? 'Closes Today' : days + 'd left'} (${item.apply_by})</span>`;
          } else if (days !== null) {
            deadlineBadge = `<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60 font-mono text-[10px]">${item.apply_by}</span>`;
          } else {
            deadlineBadge = `<span class="px-2 py-0.5 rounded bg-cyan-950/40 text-cyan-300 border border-cyan-800/40 font-mono text-[10px]">Rolling / Open</span>`;
          }

          const tagsHtml = (item.tags || []).slice(0, 4).map(t => 
            `<span class="px-2 py-0.5 rounded bg-slate-900/90 text-slate-300 border border-slate-800 font-mono text-[10px]">${t}</span>`
          ).join('');

          const isNew = item.is_new_today ? `<span class="px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-400/40 text-[9px] font-mono font-bold tracking-wider uppercase">NEW</span>` : '';

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
                <a href="${item.link}" target="_blank" rel="noopener" class="font-sans font-bold text-white text-base hover:text-cyan-400 transition flex items-start justify-between gap-2 group-hover:translate-x-0.5">
                  <span>${item.title}</span>
                  <svg class="w-4 h-4 text-slate-500 shrink-0 mt-1 opacity-70 group-hover:opacity-100 group-hover:text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
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

    // Attach dynamic event listeners
    function attachInteractiveListeners() {
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
          c.classList.remove('border-cyan-400', 'bg-cyan-500/10', 'text-cyan-300', 'font-medium');
          c.classList.add('border-slate-800', 'bg-slate-900/80', 'text-slate-300');
        });
        chip.classList.add('border-cyan-400', 'bg-cyan-500/10', 'text-cyan-300', 'font-medium');
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
    document.getElementById('toggle-hide-expired').addEventListener('change', render);

    // Update KPI Counters
    function updateCounters() {
      const activeItems = RAW_DATA.filter(d => !d.is_expired);
      const expiredItems = RAW_DATA.filter(d => d.is_expired);

      document.getElementById('stat-active').textContent = activeItems.length;
      document.getElementById('badge-active-count').textContent = activeItems.length;
      document.getElementById('stat-expired').textContent = expiredItems.length;
      document.getElementById('stat-high-stipend').textContent = activeItems.filter(d => (d.stipend_amount || 0) >= 20000).length;
      document.getElementById('stat-urgent').textContent = activeItems.filter(d => {
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
    unlisted_cutoff = (date.today() - timedelta(days=7)).isoformat()

    # IST Time formatting
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST)
    ist_formatted = now_ist.strftime("%d %b %Y, %I:%M %p IST")

    items = []
    for iid, rec in internships.items():
        raw_apply_by = (rec.get("apply_by") or "").strip()
        apply_iso = _parse_deadline_to_iso(raw_apply_by)
        last_seen = (rec.get("last_seen_at") or "")[:10]
        first_seen = (rec.get("first_seen_at") or "")[:10]

        # Determine exact expiration state
        if apply_iso:
            is_expired = apply_iso < today
            deadline_label = raw_apply_by
        else:
            # No explicit date
            # If the scraper actively spotted it on the site within the last 7 days, it is LIVE & ACTIVE!
            if last_seen and last_seen >= unlisted_cutoff:
                is_expired = False
                deadline_label = "Rolling / Active"
            else:
                # Dropped off the search results for more than a week
                is_expired = True
                deadline_label = "Closed / Unlisted"

        app = applications.get(iid, {})
        status = app.get("status", "not_applied")

        items.append({
            "id": iid,
            "title": rec.get("title", "Untitled Software Intern"),
            "company": rec.get("company", "Unknown"),
            "location": rec.get("location", "Not specified"),
            "stipend_text": rec.get("stipend_text", "Competitive"),
            "stipend_amount": rec.get("stipend_amount", 0),
            "apply_by": deadline_label,
            "apply_by_iso": apply_iso,
            "is_expired": is_expired,
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
    html = html.replace("__GENERATED_AT__", ist_formatted)
    html = html.replace("__WARN_DAYS__", str(DEADLINE_WARNING_DAYS))

    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Refreshed high-performance dashboard written to {out_path} ({len(items)} CSE listings, Sync time: {ist_formatted})")


if __name__ == "__main__":
    build()
