"""
Email Finder + AI Personalization Engine
Finds emails via Hunter.io API and generates personalized outreach with Claude
"""

import requests
import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class EmailFinder:
    """
    Multi-method email finder:
    1. Already extracted from website scrape
    2. Hunter.io API lookup
    3. Common pattern guessing
    """

    COMMON_PATTERNS = [
        "info@{domain}",
        "contact@{domain}",
        "hello@{domain}",
        "admin@{domain}",
        "office@{domain}",
        "team@{domain}",
    ]

    def __init__(self, hunter_api_key: str = ""):
        self.hunter_api_key = hunter_api_key

    def find_email(self, lead) -> str:
        """Try all methods to find email"""
        # Already have it from scrape
        if lead.email:
            return lead.email

        # Try Hunter.io
        if self.hunter_api_key and lead.website:
            email = self._hunter_lookup(lead.website)
            if email:
                lead.email = email
                return email

        return ""

    def _hunter_lookup(self, website: str) -> str:
        """Hunter.io domain search"""
        try:
            domain = website.replace("https://", "").replace("http://", "").split("/")[0]
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.hunter_api_key}&limit=1"
            resp = requests.get(url, timeout=10)
            data = resp.json()

            emails = data.get("data", {}).get("emails", [])
            if emails:
                # Prefer decision-maker roles
                for role in ["owner", "ceo", "founder", "director", "managing", "partner"]:
                    for e in emails:
                        if role in (e.get("position") or "").lower():
                            return e["value"]
                return emails[0]["value"]
        except Exception as e:
            logger.warning(f"Hunter lookup failed: {e}")
        return ""

    def verify_email_format(self, email: str) -> bool:
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        return bool(re.match(pattern, email))


class AIPersonalizer:
    """
    Uses Claude API to generate highly personalized cold emails
    for each lead based on their business data
    """

    def __init__(self, api_key: str, your_name: str = "Mordecai",
                 your_website: str = "mordecai.web.app",
                 your_email: str = "Mordecai.a.d@gmail.com",
                 service_description: str = "",
                 email_template: str = ""):
        self.api_key = api_key
        self.your_name = your_name
        self.your_website = your_website
        self.your_email = your_email
        self.service_description = service_description or (
            "I build AI chatbots and RAG systems that help businesses automate "
            "customer support, handle FAQs, and save staff time."
        )
        self.email_template = email_template

    def generate_email(self, lead) -> str:
        """Generate a personalized cold email for this lead"""
        if not self.api_key:
            return self._template_fallback(lead)

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            lead_info = f"""
Business Name: {lead.name}
Category: {lead.category}
Location: {lead.address}
Rating: {lead.rating} stars ({lead.review_count} reviews)
Website: {lead.website}
Has existing chatbot: {lead.has_chatbot} ({lead.chatbot_type if lead.has_chatbot else "none"})
Has FAQ page: {lead.faq_page}
Tech stack: {', '.join(lead.tech_stack) or 'unknown'}
"""

            custom_template_instruction = ""
            if self.email_template:
                custom_template_instruction = f"""
The user has provided this template as a guide:
---
{self.email_template}
---
Adapt this template for the specific business, keeping the structure but personalizing the content.
"""

            system_prompt = f"""You are an expert cold email copywriter. Write highly personalized, 
concise cold emails that get replies. 

The sender is: {self.your_name}
Sender website: {self.your_website}  
Sender email: {self.your_email}
Sender service: {self.service_description}

Rules:
- NEVER use "I hope this email finds you well" or similar openers
- First sentence must reference something SPECIFIC about this business
- Focus on ONE pain point they likely have
- Keep it under 150 words
- End with a soft CTA (10-minute call or question)
- Sound like a real person, not a marketer
- Include subject line first, then email body
- Format: Subject: [subject line]\n\n[email body]
{custom_template_instruction}"""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Write a cold email for this business:\n{lead_info}"
                }]
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"AI email generation failed: {e}")
            return self._template_fallback(lead)

    def generate_personalization_note(self, lead) -> str:
        """Generate a one-liner personalization note for manual emails"""
        if not self.api_key:
            return ""

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": f"""Write ONE sentence (max 20 words) that opens a cold email to {lead.name}, 
a {lead.category} in {lead.address} with {lead.review_count} reviews and {"a FAQ page" if lead.faq_page else "no FAQ page"}.
Reference something specific about their business that shows you've done research.
Output only the sentence, nothing else."""
                }]
            )
            return message.content[0].text.strip()

        except:
            return ""

    def _template_fallback(self, lead) -> str:
        """Fallback template when no API key"""
        subject = f"Quick question about {lead.name}'s customer inquiries"
        body = f"""Hi,

I came across {lead.name} while looking for {lead.category.lower()}s in {lead.address}.

I noticed your website likely handles a lot of repetitive customer questions — I build AI assistants that answer them automatically, 24/7, trained on your specific business information.

I recently built one for a client that cut their response time from hours to instant.

Would a 10-minute call make sense this week?

{self.your_name}
{self.your_website}
{self.your_email}"""
        return f"Subject: {subject}\n\n{body}"
