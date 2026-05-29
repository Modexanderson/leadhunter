"""
Core Scraper Engine - Google Maps + Website Analysis
v2 - Fixed name extraction, email filtering, rate limit handling
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
    status: str = "new"


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
    "Generic Widget": ["chat-widget", "livesupport"],
}

# Strict email pattern - must have proper TLD
EMAIL_REGEX = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b'
)

# Things that look like emails but aren't
EMAIL_BLACKLIST = [
    "example", "test", "noreply", "no-reply", "privacy",
    "support@wordpress", "@sentry", ".png", ".jpg", ".webp",
    ".gif", ".svg", ".ico", "@2x", "schema", "namespace",
    "xml", "xsd", "dtd", "placeholder", "youremail", "user@",
    "email@", "name@", "info@domain", "@domain.com"
]

CONTACT_PAGE_HINTS = [
    "contact", "contact-us", "get-in-touch", "reach-us",
    "about", "about-us", "team", "staff", "attorneys",
    "lawyers", "agents", "realtors"
]


def is_valid_email(email: str) -> bool:
    """Strict email validation - filters out image filenames, placeholders etc."""
    email_lower = email.lower()
    # Must match proper format
    if not EMAIL_REGEX.match(email):
        return False
    # Blacklist check
    if any(b in email_lower for b in EMAIL_BLACKLIST):
        return False
    # Domain must have at least one dot and real TLD
    parts = email.split("@")
    if len(parts) != 2:
        return False
    domain = parts[1]
    if "." not in domain:
        return False
    tld = domain.split(".")[-1].lower()
    if len(tld) < 2 or len(tld) > 6:
        return False
    # No image extensions in domain
    if any(domain.endswith(ext) for ext in [".png", ".jpg", ".webp", ".gif", ".svg"]):
        return False
    return True


class ScraperEngine:
    def __init__(self, config: dict, progress_callback=None, log_callback=None):
        self.config = config
        self.progress_callback = progress_callback or (lambda *a: None)
        self.log_callback = log_callback or (lambda msg, level="info": None)
        self.leads: list[Lead] = []
        self.running = False
        self._stop_flag = False

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

    def _random_ua(self) -> str:
        return random.choice(self.user_agents)

    def run_scrape(self) -> list[Lead]:
        return asyncio.run(self._scrape_all())

    async def _scrape_all(self) -> list[Lead]:
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
                    "--disable-web-security",
                ]
            )

            total_cities = len(cities)
            consecutive_failures = 0

            for city_idx, city in enumerate(cities):
                if self._stop_flag:
                    break

                # If 3+ cities in a row failed, take a long break
                if consecutive_failures >= 3:
                    wait = random.uniform(45, 90)
                    self._log(f"⏸️ Google rate limit detected. Waiting {wait:.0f}s...", "warning")
                    await asyncio.sleep(wait)
                    consecutive_failures = 0

                    # Rotate browser context (new fingerprint)
                    await browser.close()
                    browser = await p.chromium.launch(
                        headless=self.config.get("headless", True),
                        args=["--no-sandbox", "--disable-blink-features=AutomationControlled",
                              "--disable-infobars", "--disable-dev-shm-usage"]
                    )

                # Fresh context per city = different fingerprint
                context = await browser.new_context(
                    user_agent=self._random_ua(),
                    viewport={"width": random.choice([1280, 1366, 1440, 1920]),
                              "height": random.choice([720, 768, 900, 1080])},
                    locale="en-US",
                    timezone_id=random.choice([
                        "America/Chicago", "America/New_York",
                        "America/Los_Angeles", "America/Denver"
                    ]),
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "DNT": "1",
                    }
                )

                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    window.chrome = {runtime: {}};
                """)

                self._log(f"🏙️ Scraping {business_type} in {city}...", "info")

                try:
                    city_leads = await self._scrape_google_maps(
                        context, business_type, city, max_per_city
                    )

                    if city_leads:
                        consecutive_failures = 0
                        self._log(f"✅ Found {len(city_leads)} businesses in {city}", "success")
                    else:
                        consecutive_failures += 1

                    for i, lead in enumerate(city_leads):
                        if self._stop_flag:
                            break
                        if lead.website:
                            self._log(f"🔍 Analyzing {lead.name}...", "info")
                            await self._analyze_website(context, lead)
                            lead.score = self._score_lead(lead)
                            delay = random.uniform(
                                self.config.get("min_delay", 1.5),
                                self.config.get("max_delay", 4.0)
                            )
                            await asyncio.sleep(delay)

                        self.leads.append(lead)
                        progress = ((city_idx * max_per_city + i + 1) /
                                    (total_cities * max_per_city)) * 100
                        self.progress_callback(progress, lead)

                except Exception as e:
                    self._log(f"❌ Error in {city}: {e}", "error")
                    consecutive_failures += 1
                finally:
                    await context.close()

                # Between cities: random human pause
                if city_idx < total_cities - 1 and not self._stop_flag:
                    pause = random.uniform(3, 8)
                    await asyncio.sleep(pause)

            await browser.close()

        self.running = False
        self._log(f"🎉 Scraping complete. {len(self.leads)} total leads found.", "success")
        return self.leads

    async def _scrape_google_maps(self, context, business_type: str, city: str, max_results: int) -> list[Lead]:
        page = await context.new_page()
        leads = []

        try:
            query = f"{business_type} {city}"
            maps_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

            # Use domcontentloaded instead of networkidle - much more reliable
            await page.goto(maps_url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(random.uniform(3, 5))

            # Check if we hit a captcha or error page
            page_content = await page.content()
            if "unusual traffic" in page_content.lower() or "captcha" in page_content.lower():
                self._log(f"⚠️ CAPTCHA detected for {city} — skipping", "warning")
                return leads

            # Wait for results panel
            try:
                await page.wait_for_selector('[role="feed"]', timeout=15000)
            except:
                self._log(f"   No results panel found for {city}", "warning")
                return leads

            # Scroll to load results
            scroll_count = max(2, max_results // 5)
            for _ in range(scroll_count):
                if self._stop_flag:
                    break
                try:
                    await page.evaluate("""
                        const feed = document.querySelector('[role="feed"]');
                        if (feed) feed.scrollBy(0, 1000);
                    """)
                    await asyncio.sleep(random.uniform(1.5, 2.5))
                except:
                    pass

            # Get all place links
            listings = await page.locator('a[href*="/maps/place/"]').all()
            self._log(f"   Found {len(listings)} listing elements", "info")

            seen_names = set()

            for listing in listings[:max_results * 2]:  # Get extras to account for dupes
                if self._stop_flag or len(leads) >= max_results:
                    break
                try:
                    await listing.click()
                    await asyncio.sleep(random.uniform(2.0, 3.5))

                    lead = await self._extract_place_details(page, city)
                    if lead and lead.name and lead.name not in seen_names and lead.name != "Results":
                        seen_names.add(lead.name)
                        leads.append(lead)
                        self._log(f"   ✓ {lead.name} | ⭐{lead.rating} ({lead.review_count} reviews)", "info")

                except Exception as e:
                    pass  # Skip silently, don't spam the log

            # Filter by review count
            min_reviews = self.config.get("min_reviews", 0)
            max_reviews = self.config.get("max_reviews", 500)
            leads = [l for l in leads if min_reviews <= l.review_count <= max_reviews]

        except Exception as e:
            self._log(f"Maps scrape error: {e}", "error")
        finally:
            await page.close()

        return leads

    async def _extract_place_details(self, page, city: str) -> Optional[Lead]:
        lead = Lead()
        lead.address = city

        try:
            # Wait a moment for panel to load
            await asyncio.sleep(0.5)

            # NAME - try multiple selectors
            name = ""
            for selector in [
                'h1.DUwDvf',          # Common Maps class
                'h1[class*="fontHeadline"]',
                'h1[class*="DUwDvf"]',
                '.qBF1Pd',            # Another common name class
                'h1',                 # Fallback
            ]:
                try:
                    el = page.locator(selector).first
                    if await el.count() > 0:
                        text = (await el.inner_text()).strip()
                        if text and text != "Results" and len(text) > 1:
                            name = text
                            break
                except:
                    pass

            # If h1 still gives "Results", try getting name from URL
            if not name or name == "Results":
                try:
                    url = page.url
                    if "/maps/place/" in url:
                        # URL format: /maps/place/Business+Name/@lat,lng
                        place_part = url.split("/maps/place/")[1].split("/")[0]
                        place_part = place_part.split("@")[0]
                        name = place_part.replace("+", " ").replace("%20", " ").strip()
                except:
                    pass

            lead.name = name

            # RATING
            try:
                for selector in ['[aria-label*="stars"]', '[aria-label*="star"]']:
                    els = await page.locator(selector).all()
                    for el in els:
                        aria = await el.get_attribute("aria-label") or ""
                        match = re.search(r'([\d.]+)\s*star', aria)
                        if match:
                            lead.rating = float(match.group(1))
                            break
                    if lead.rating:
                        break
            except:
                pass

            # REVIEW COUNT
            try:
                for selector in ['[aria-label*="review"]', 'button[aria-label*="review"]']:
                    els = await page.locator(selector).all()
                    for el in els:
                        aria = await el.get_attribute("aria-label") or ""
                        match = re.search(r'([\d,]+)\s*review', aria)
                        if match:
                            lead.review_count = int(match.group(1).replace(",", ""))
                            break
                    if lead.review_count:
                        break
            except:
                pass

            # PHONE
            try:
                for selector in ['[data-tooltip="Copy phone number"]', '[aria-label*="phone"]']:
                    el = page.locator(selector).first
                    if await el.count() > 0:
                        lead.phone = (await el.inner_text()).strip()
                        break
            except:
                pass

            # WEBSITE
            try:
                for selector in [
                    'a[data-tooltip="Open website"]',
                    'a[aria-label*="website" i]',
                    'a[href*="http"]:not([href*="google"]):not([href*="maps"])',
                ]:
                    el = page.locator(selector).first
                    if await el.count() > 0:
                        href = await el.get_attribute("href") or ""
                        if href.startswith("http") and "google.com" not in href:
                            lead.website = href
                            break
            except:
                pass

            # ADDRESS
            try:
                for selector in ['[data-tooltip="Copy address"]', '[aria-label*="address"]']:
                    el = page.locator(selector).first
                    if await el.count() > 0:
                        addr = (await el.inner_text()).strip()
                        if addr:
                            lead.address = addr
                            break
            except:
                pass

            # CATEGORY
            try:
                for selector in ['button[jsaction*="category"]', '.skqShb', '[class*="category"]']:
                    el = page.locator(selector).first
                    if await el.count() > 0:
                        cat = (await el.inner_text()).strip()
                        if cat and len(cat) < 50:
                            lead.category = cat
                            break
            except:
                pass

            lead.maps_url = page.url

        except Exception as e:
            self._log(f"Detail extraction error: {e}", "warning")

        return lead

    async def _analyze_website(self, context, lead: Lead):
        if not lead.website or not lead.website.startswith("http"):
            return

        page = await context.new_page()

        try:
            await page.goto(lead.website, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(random.uniform(0.8, 1.5))

            html = await page.content()
            html_lower = html.lower()

            # Chatbot detection
            for bot_name, patterns in CHATBOT_PATTERNS.items():
                if any(p in html_lower for p in patterns):
                    lead.has_chatbot = True
                    lead.chatbot_type = bot_name
                    break

            # Email extraction - strict filtering
            raw_emails = EMAIL_REGEX.findall(html)
            valid_emails = [e for e in raw_emails if is_valid_email(e)]
            if valid_emails:
                lead.email = valid_emails[0]

            # Tech stack
            tech = []
            tech_patterns = {
                "WordPress": ["wp-content", "wp-includes"],
                "Shopify": ["cdn.shopify"],
                "Wix": ["wix.com", "wixstatic"],
                "Squarespace": ["squarespace"],
                "Webflow": ["webflow.io"],
                "React/Next.js": ["__NEXT_DATA__", "react.development"],
                "HubSpot CMS": ["hs-sites"],
            }
            for tech_name, patterns in tech_patterns.items():
                if any(p in html_lower for p in patterns):
                    tech.append(tech_name)
            lead.tech_stack = tech

            # FAQ detection
            if any(x in html_lower for x in ["frequently asked", "faq", "common questions"]):
                lead.faq_page = True

            # Visit contact page if no email yet
            if not lead.email:
                try:
                    all_links = await page.locator("a[href]").all()
                    contact_hrefs = []
                    for link in all_links[:60]:
                        try:
                            href = await link.get_attribute("href") or ""
                            text = (await link.inner_text()).lower().strip()
                            if any(hint in href.lower() or hint in text for hint in CONTACT_PAGE_HINTS):
                                full_url = urljoin(lead.website, href)
                                if urlparse(full_url).netloc == urlparse(lead.website).netloc:
                                    if full_url not in contact_hrefs:
                                        contact_hrefs.append(full_url)
                        except:
                            pass

                    if contact_hrefs:
                        await page.goto(contact_hrefs[0], wait_until="domcontentloaded", timeout=15000)
                        await asyncio.sleep(0.8)
                        contact_html = await page.content()
                        raw_emails = EMAIL_REGEX.findall(contact_html)
                        valid = [e for e in raw_emails if is_valid_email(e)]
                        if valid:
                            lead.email = valid[0]
                            lead.contact_page = contact_hrefs[0]
                except:
                    pass

            # Social links
            social_patterns = {
                "linkedin": r'https?://(?:www\.)?linkedin\.com/(?:company|in)/[\w.-]+',
                "twitter": r'https?://(?:www\.)?(?:twitter|x)\.com/[\w.-]+',
                "facebook": r'https?://(?:www\.)?facebook\.com/[\w.-]+',
            }
            for soc, pattern in social_patterns.items():
                match = re.search(pattern, html)
                if match:
                    lead.social_links[soc] = match.group(0)

        except Exception as e:
            self._log(f"Website analysis error for {lead.website}: {e}", "warning")
        finally:
            await page.close()

    def _score_lead(self, lead: Lead) -> int:
        score = 50
        if lead.email:
            score += 20
        if not lead.has_chatbot:
            score += 15
        else:
            score -= 20
        if 10 <= lead.review_count <= 200:
            score += 10
        elif lead.review_count > 500:
            score -= 15
        elif lead.review_count < 5:
            score -= 10
        if lead.faq_page:
            score += 10
        if lead.website:
            score += 5
        if lead.rating >= 4.0:
            score += 5
        if "WordPress" in lead.tech_stack:
            score += 5
        return max(0, min(100, score))
