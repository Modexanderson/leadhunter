"""
Core Scraper Engine - Google Maps + Website Analysis
Handles all data extraction with anti-detection measures
"""

import asyncio
import random
import time
import re
import json
import logging
from typing import Optional
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


@dataclass
class Lead:
    """Represents a business lead"""
    name: str = ""
    address: str = ""
    phone: str = ""
    website: str = ""
    rating: float = 0.0
    review_count: int = 0
    category: str = ""
    maps_url: str = ""
    email: str = ""
    contact_page: str = ""
    has_chatbot: bool = False
    chatbot_type: str = ""
    website_age_hint: str = ""
    staff_count_hint: str = ""
    social_links: dict = field(default_factory=dict)
    tech_stack: list = field(default_factory=list)
    faq_page: bool = False
    personalization_note: str = ""
    ai_email_draft: str = ""
    score: int = 0
    status: str = "new"  # new, emailed, replied, converted, rejected


# Chatbot detection patterns
CHATBOT_PATTERNS = {
    "Intercom": ["intercom", "intercomcdn"],
    "Drift": ["drift.com", "js.driftt.com"],
    "Zendesk": ["zendesk", "zopim"],
    "Tidio": ["tidio"],
    "LiveChat": ["livechatinc", "livechat"],
    "Freshchat": ["freshchat", "freshworks"],
    "HubSpot": ["hubspot", "hs-scripts"],
    "Crisp": ["crisp.chat"],
    "Tawk.to": ["tawk.to"],
    "Olark": ["olark"],
    "Chaport": ["chaport"],
    "ChatBot": ["chatbot.com"],
    "ManyChat": ["manychat"],
    "Generic Widget": ["chatbot", "chat-widget", "live-chat", "livesupport"],
}

EMAIL_PATTERNS = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
]

# Pages likely to contain contact info
CONTACT_PAGE_HINTS = [
    "contact", "contact-us", "get-in-touch", "reach-us",
    "about", "about-us", "team", "staff", "attorneys",
    "lawyers", "agents", "realtors"
]


class ScraperEngine:
    """
    Advanced async scraper with anti-detection, retry logic,
    and intelligent lead scoring
    """

    def __init__(self, config: dict, progress_callback=None, log_callback=None):
        self.config = config
        self.progress_callback = progress_callback or (lambda *a: None)
        self.log_callback = log_callback or (lambda msg, level="info": None)
        self.leads: list[Lead] = []
        self.running = False
        self._stop_flag = False

        # Load user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        ]

    def stop(self):
        self._stop_flag = True

    def _log(self, msg: str, level: str = "info"):
        logger.info(msg)
        self.log_callback(msg, level)

    def _random_delay(self, min_s: float = None, max_s: float = None):
        min_s = min_s or self.config.get("min_delay", 1.5)
        max_s = max_s or self.config.get("max_delay", 4.0)
        delay = random.uniform(min_s, max_s)
        time.sleep(delay)

    def _random_ua(self) -> str:
        return random.choice(self.user_agents)

    def run_scrape(self) -> list[Lead]:
        """Main entry point - runs async scrape in sync context"""
        return asyncio.run(self._scrape_all())

    async def _scrape_all(self) -> list[Lead]:
        """Orchestrates the full scraping pipeline"""
        from playwright.async_api import async_playwright

        self.running = True
        self._stop_flag = False
        self.leads = []

        business_type = self.config["business_type"]
        cities = self.config["cities"]
        max_per_city = self.config.get("max_per_city", 20)

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.config.get("headless", True),
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--disable-dev-shm-usage",
                ]
            )

            context = await browser.new_context(
                user_agent=self._random_ua(),
                viewport={"width": 1366, "height": 768},
                locale="en-US",
                timezone_id="America/Chicago",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }
            )

            # Anti-detection: remove navigator.webdriver
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = {runtime: {}};
            """)

            total_cities = len(cities)
            for city_idx, city in enumerate(cities):
                if self._stop_flag:
                    break

                self._log(f"🏙️ Scraping {business_type} in {city}...", "info")
                query = f"{business_type} {city}"

                try:
                    city_leads = await self._scrape_google_maps(
                        context, query, max_per_city, city
                    )
                    self._log(f"✅ Found {len(city_leads)} businesses in {city}", "success")

                    # Visit each website
                    for i, lead in enumerate(city_leads):
                        if self._stop_flag:
                            break
                        if lead.website:
                            self._log(f"🔍 Analyzing {lead.name}...", "info")
                            await self._analyze_website(context, lead)
                            lead.score = self._score_lead(lead)
                            await asyncio.sleep(random.uniform(1.0, 2.5))

                        self.leads.append(lead)
                        progress = ((city_idx * max_per_city + i + 1) /
                                    (total_cities * max_per_city)) * 100
                        self.progress_callback(progress, lead)

                except Exception as e:
                    self._log(f"❌ Error in {city}: {e}", "error")

            await browser.close()

        self.running = False
        self._log(f"🎉 Scraping complete. {len(self.leads)} total leads found.", "success")
        return self.leads

    async def _scrape_google_maps(self, context, query: str, max_results: int, city: str) -> list[Lead]:
        """Scrapes Google Maps search results"""
        page = await context.new_page()
        leads = []

        try:
            maps_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
            await page.goto(maps_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(random.uniform(2, 4))

            # Scroll to load more results
            results_panel = page.locator('[role="feed"]')
            scroll_count = max(3, max_results // 7)

            for _ in range(scroll_count):
                if self._stop_flag:
                    break
                try:
                    await results_panel.evaluate("el => el.scrollBy(0, 800)")
                    await asyncio.sleep(random.uniform(1.5, 3.0))
                except:
                    pass

            # Extract listings
            listings = await page.locator('[role="feed"] > div > div > a[href*="/maps/place/"]').all()
            self._log(f"   Found {len(listings)} listing elements", "info")

            for listing in listings[:max_results]:
                if self._stop_flag:
                    break
                try:
                    href = await listing.get_attribute("href")
                    await listing.click()
                    await asyncio.sleep(random.uniform(1.5, 2.5))

                    lead = await self._extract_place_details(page, city)
                    if lead and lead.name:
                        leads.append(lead)
                        self._log(f"   ✓ {lead.name} | ⭐{lead.rating} ({lead.review_count} reviews)", "info")

                except Exception as e:
                    self._log(f"   ⚠️ Skipped listing: {e}", "warning")

            # Filter by review count thresholds
            min_reviews = self.config.get("min_reviews", 0)
            max_reviews = self.config.get("max_reviews", 500)
            leads = [l for l in leads if min_reviews <= l.review_count <= max_reviews]

        except Exception as e:
            self._log(f"Maps scrape error: {e}", "error")
        finally:
            await page.close()

        return leads

    async def _extract_place_details(self, page, city: str) -> Optional[Lead]:
        """Extracts all available details from a Maps place panel"""
        lead = Lead()
        lead.address = city

        try:
            # Name
            name_el = page.locator('h1').first
            if await name_el.count() > 0:
                lead.name = (await name_el.inner_text()).strip()

            # Rating
            try:
                rating_el = page.locator('[aria-label*="stars"]').first
                if await rating_el.count() > 0:
                    aria = await rating_el.get_attribute("aria-label") or ""
                    match = re.search(r'([\d.]+)\s*star', aria)
                    if match:
                        lead.rating = float(match.group(1))
            except:
                pass

            # Review count
            try:
                review_els = await page.locator('[aria-label*="review"]').all()
                for el in review_els:
                    aria = await el.get_attribute("aria-label") or ""
                    match = re.search(r'([\d,]+)\s*review', aria)
                    if match:
                        lead.review_count = int(match.group(1).replace(",", ""))
                        break
            except:
                pass

            # Phone
            try:
                phone_el = page.locator('[data-tooltip="Copy phone number"]').first
                if await phone_el.count() > 0:
                    lead.phone = (await phone_el.inner_text()).strip()
            except:
                pass

            # Website
            try:
                website_el = page.locator('a[data-tooltip="Open website"]').first
                if await website_el.count() == 0:
                    website_el = page.locator('a[aria-label*="website" i]').first
                if await website_el.count() > 0:
                    lead.website = await website_el.get_attribute("href") or ""
            except:
                pass

            # Address
            try:
                addr_el = page.locator('[data-tooltip="Copy address"]').first
                if await addr_el.count() > 0:
                    lead.address = (await addr_el.inner_text()).strip()
            except:
                pass

            # Category
            try:
                # Usually the first button-like element below the name
                cat_els = await page.locator('[jsaction*="pane.rating"] button').all()
                if cat_els:
                    lead.category = (await cat_els[0].inner_text()).strip()
            except:
                pass

            lead.maps_url = page.url

        except Exception as e:
            self._log(f"Detail extraction error: {e}", "warning")

        return lead

    async def _analyze_website(self, context, lead: Lead):
        """Deep website analysis: emails, chatbots, tech stack, FAQ"""
        if not lead.website or not lead.website.startswith("http"):
            return

        page = await context.new_page()

        try:
            await page.goto(lead.website, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(random.uniform(1.0, 2.0))

            html = await page.content()
            html_lower = html.lower()

            # --- Chatbot detection ---
            for bot_name, patterns in CHATBOT_PATTERNS.items():
                if any(p in html_lower for p in patterns):
                    lead.has_chatbot = True
                    lead.chatbot_type = bot_name
                    break

            # --- Email extraction from homepage ---
            emails = re.findall(EMAIL_PATTERNS[0], html)
            filtered = [e for e in emails if not any(x in e.lower() for x in
                        ["example", "test", "noreply", "no-reply", "privacy", "support@wordpress", "@sentry"])]
            if filtered:
                lead.email = filtered[0]

            # --- Tech stack hints ---
            tech = []
            tech_patterns = {
                "WordPress": ["wp-content", "wp-includes"],
                "Shopify": ["cdn.shopify"],
                "Wix": ["wix.com", "wixstatic"],
                "Squarespace": ["squarespace"],
                "Webflow": ["webflow.io", "webflow.com/"],
                "React": ["react.development", "__NEXT_DATA__"],
                "Angular": ["ng-version"],
                "HubSpot CMS": ["hs-sites"],
            }
            for tech_name, patterns in tech_patterns.items():
                if any(p in html_lower for p in patterns):
                    tech.append(tech_name)
            lead.tech_stack = tech

            # --- FAQ page detection ---
            if any(x in html_lower for x in ["frequently asked", "faq", "common questions"]):
                lead.faq_page = True

            # --- Find and visit contact page ---
            all_links = await page.locator("a[href]").all()
            contact_hrefs = []
            for link in all_links[:50]:
                try:
                    href = await link.get_attribute("href") or ""
                    text = (await link.inner_text()).lower()
                    if any(hint in href.lower() or hint in text for hint in CONTACT_PAGE_HINTS):
                        full_url = urljoin(lead.website, href)
                        if urlparse(full_url).netloc == urlparse(lead.website).netloc:
                            contact_hrefs.append(full_url)
                except:
                    pass

            # Visit first contact page if no email found yet
            if contact_hrefs and not lead.email:
                try:
                    await page.goto(contact_hrefs[0], wait_until="domcontentloaded", timeout=15000)
                    await asyncio.sleep(0.8)
                    contact_html = await page.content()
                    emails = re.findall(EMAIL_PATTERNS[0], contact_html)
                    filtered = [e for e in emails if not any(x in e.lower() for x in
                                ["example", "test", "noreply", "no-reply"])]
                    if filtered:
                        lead.email = filtered[0]
                        lead.contact_page = contact_hrefs[0]
                except:
                    pass

            # Social links
            social_patterns = {
                "linkedin": "linkedin.com",
                "twitter": "twitter.com",
                "facebook": "facebook.com",
                "instagram": "instagram.com",
            }
            for soc, domain in social_patterns.items():
                if domain in html_lower:
                    # Try to extract actual URL
                    match = re.search(rf'https?://(?:www\.)?{re.escape(domain)}/[\w.-]+', html)
                    if match:
                        lead.social_links[soc] = match.group(0)

        except Exception as e:
            self._log(f"Website analysis error for {lead.website}: {e}", "warning")
        finally:
            await page.close()

    def _score_lead(self, lead: Lead) -> int:
        """
        Scores a lead 0-100 based on how good a prospect they are.
        High score = better target.
        """
        score = 50  # Base

        # Has email = very valuable
        if lead.email:
            score += 20

        # No existing chatbot = needs one
        if not lead.has_chatbot:
            score += 15
        else:
            score -= 20  # Already has solution

        # Sweet spot: 10-200 reviews (not too small, not too big)
        if 10 <= lead.review_count <= 200:
            score += 10
        elif lead.review_count > 500:
            score -= 15  # Too big
        elif lead.review_count < 5:
            score -= 10  # Too small / dormant

        # Has FAQ page = clearly needs chatbot
        if lead.faq_page:
            score += 10

        # Has website = can integrate
        if lead.website:
            score += 5

        # Good rating = successful business, has budget
        if lead.rating >= 4.0:
            score += 5

        # WordPress = easy to add chatbot plugin / widget
        if "WordPress" in lead.tech_stack:
            score += 5

        return max(0, min(100, score))
