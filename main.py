"""
LeadHunter Pro - AI-Powered Business Lead Scraper & Outreach System
By Mordecai | mordecai.web.app
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import LeadHunterApp

if __name__ == "__main__":
    app = LeadHunterApp()
    app.run()
