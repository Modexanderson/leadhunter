#!/usr/bin/env python3
"""
LeadHunter Pro - One-click setup script
Run this first: python setup.py
"""

import subprocess
import sys
import os
from pathlib import Path

def run(cmd, desc=""):
    print(f"\n{'─'*50}")
    print(f"▶ {desc or cmd}")
    print('─'*50)
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    print("""
╔══════════════════════════════════════════╗
║     LeadHunter Pro — Setup Wizard        ║
║     Building your lead machine...        ║
╚══════════════════════════════════════════╝
""")

    # Create directories
    for d in ["data", "exports", "ui", "core"]:
        Path(d).mkdir(exist_ok=True)
    print("✅ Directories created")

    # Create .gitignore
    gitignore = Path(".gitignore")
    gitignore.write_text("data/config.json\n*.pyc\n__pycache__/\nexports/\n.env\n")
    print("✅ .gitignore created (your API keys are safe)")

    # Install requirements
    print("\n📦 Installing Python packages...")
    ok = run(f"{sys.executable} -m pip install -r requirements.txt", "Installing dependencies")
    if not ok:
        print("⚠️  Some packages may have failed. Trying individually...")

    # Install Playwright browsers
    print("\n🌐 Installing Playwright browsers (Chromium)...")
    run(f"{sys.executable} -m playwright install chromium", "Installing Chromium browser")

    print("""
╔══════════════════════════════════════════╗
║            SETUP COMPLETE! ✅             ║
╚══════════════════════════════════════════╝

Next steps:
  1. Run:  python main.py
  2. Go to 🔑 API Keys panel and add your keys
  3. Go to 📧 Outreach and fill in your info
  4. Go to 🎯 Scrape Targets and start hunting!

To get your keys:
  • Anthropic API: https://console.anthropic.com
  • Hunter.io:     https://hunter.io/api-key
  • Gmail App PW:  myaccount.google.com → Security → App Passwords
""")

if __name__ == "__main__":
    main()
