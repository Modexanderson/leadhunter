# ⚡ LeadHunter Pro
### AI-Powered Business Lead Generation & Cold Outreach System
*Built by Mordecai | mordecai.web.app*

---

## What This Does

LeadHunter Pro is a full desktop application that:

1. **Scrapes Google Maps** for businesses matching your target (law firms, dental clinics, etc.) in any city
2. **Visits each website** to extract emails, detect existing chatbots, analyze tech stack, find FAQ pages
3. **Scores every lead 0–100** based on how likely they are to buy from you
4. **Uses Claude AI** to write a personalized cold email for each lead
5. **Sends the emails** via Gmail with human-like delays to avoid spam filters

---

## Quick Start

```bash
# 1. Run setup (installs everything)
python setup.py

# 2. Launch the app
python main.py
```

---

## First-Time Setup

### Step 1 — API Keys (`🔑 API Keys` panel)

| Key | Where to Get | Required? |
|-----|-------------|-----------|
| Anthropic API Key | [console.anthropic.com](https://console.anthropic.com) | ✅ For AI emails |
| Hunter.io API Key | [hunter.io/api-key](https://hunter.io/api-key) | Optional (extra email finding) |

### Step 2 — Your Identity (`📧 Outreach` panel)
- Fill in your name, website, email
- Write what services you offer (the AI uses this)
- Optionally customize the email template

### Step 3 — Gmail Setup (`📧 Outreach` panel)
1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Security → 2-Step Verification → Enable
3. Security → App Passwords → Create one for "LeadHunter"
4. Copy the 16-char password into the app

---

## Usage Guide

### Scraping Leads (`🎯 Scrape Targets`)

1. Select business type (e.g. `law firm`)
2. Click a city preset or type cities manually (one per line)
3. Adjust max results per city
4. Toggle filters:
   - **Skip businesses with existing chatbots** → only target fresh opportunities
   - **Require email** → only keep leads with a found email
5. Click **🚀 START HUNTING**

Watch the log panel for real-time progress.

### Generating Emails (`📧 Outreach`)

1. Click **🤖 Generate AI Emails**
2. Claude writes a personalized email for each lead using:
   - Their business name, category, location
   - Whether they have a FAQ page
   - Their review count (signals business size)
   - Your service description and template

### Sending (`📧 Outreach`)

1. Set your daily send limit (30–50/day is safe)
2. Set delays between emails (60–120 seconds minimum)
3. Click **📤 Start Sending**
4. Stop anytime with **⏹ Stop**

### Viewing & Exporting (`📊 Leads Table`)

- Filter by status: `new` → `emailed` → `replied` → `converted`
- Filter by minimum lead score
- Export to CSV or Excel
- Load previously saved JSON sessions

---

## Lead Scoring System

Leads are scored 0–100. Higher = better target.

| Factor | Points |
|--------|--------|
| Has email found | +20 |
| No existing chatbot | +15 |
| Has FAQ page | +10 |
| 10–200 reviews (right size) | +10 |
| Rating ≥ 4.0 (has budget) | +5 |
| Has website | +5 |
| WordPress site (easy install) | +5 |
| Already has chatbot | -20 |
| 500+ reviews (too big) | -15 |

**Color coding in table:**
- 🟢 Green = score ≥ 70 (hot lead)
- 🟡 Yellow = score 45–69 (warm)
- 🔴 Red = score < 45 (cold)
- 🔵 Blue = already emailed

---

## Anti-Detection Features

- Randomized user agents (rotates between 5 real browser signatures)
- Random delays between page visits (configurable min/max)
- Human-like scrolling behavior
- Removes `navigator.webdriver` flag
- Realistic browser viewport and locale settings
- Random delays between emails (configurable)

---

## File Structure

```
leadhunter/
├── main.py              # Entry point
├── setup.py             # One-click installer
├── requirements.txt     # Dependencies
├── core/
│   ├── scraper.py       # Google Maps + website analysis engine
│   ├── outreach.py      # Email finder + AI personalization
│   ├── sender.py        # Gmail SMTP sender
│   └── exporter.py      # CSV/Excel/JSON export
├── ui/
│   └── app.py           # Full desktop UI (CustomTkinter)
├── data/
│   ├── config.json      # Your keys + settings (gitignored)
│   └── send_log.json    # Email send history
└── exports/             # Your exported lead files
```

---

## Tips for Best Results

1. **Start with law firms in Chicago** — high budget, repetitive questions, WordPress sites
2. **Score ≥ 60 before emailing** — saves your daily send limit for hot leads
3. **Send 20–30 emails/day max** — slow and personal beats fast and generic
4. **Personalize the opener** — the AI does this, but review a few before bulk sending
5. **Follow up 3 days later** — most replies come from follow-ups, not first email

---

## Security

- All API keys saved locally in `data/config.json`
- This file is in `.gitignore` — never committed to Git
- No data sent anywhere except Google Maps, business websites, Hunter.io, Anthropic API, and Gmail

---

*LeadHunter Pro | Built for Mordecai's AI engineering freelance business*
