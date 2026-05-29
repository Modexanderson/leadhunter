"""
Multi-AI Outreach Engine
Supports: Claude (all versions), OpenAI GPT (all versions), 
          Google Gemini, Ollama (any local model)
"""

import requests
import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────── AI PROVIDER REGISTRY ───────────────────────

AI_PROVIDERS = {
    "Claude (Anthropic)": {
        "models": [
            "claude-opus-4-5",
            "claude-sonnet-4-5",
            "claude-haiku-4-5",
            "claude-opus-4",
            "claude-sonnet-4",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        "key_label": "Anthropic API Key",
        "key_hint": "sk-ant-...",
        "key_url": "https://console.anthropic.com",
        "recommended": "claude-sonnet-4-5",
    },
    "ChatGPT (OpenAI)": {
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-4-0125-preview",
            "gpt-4-turbo-preview",
            "o1-preview",
            "o1-mini",
        ],
        "key_label": "OpenAI API Key",
        "key_hint": "sk-...",
        "key_url": "https://platform.openai.com/api-keys",
        "recommended": "gpt-4o",
    },
    "Gemini (Google)": {
        "models": [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-pro",
        ],
        "key_label": "Google AI API Key",
        "key_hint": "AIza...",
        "key_url": "https://aistudio.google.com/app/apikey",
        "recommended": "gemini-1.5-pro",
    },
    "Ollama (Local)": {
        "models": [],  # Dynamically populated
        "key_label": "No key needed (runs locally)",
        "key_hint": "localhost:11434",
        "key_url": "https://ollama.ai",
        "recommended": "llama3.2",
    },
}

OLLAMA_SETUP_COMMANDS = """
# ─── OLLAMA SETUP GUIDE ───────────────────────────────────────────
# Install Ollama (run in terminal):
#   Windows:  winget install Ollama.Ollama
#   Mac:      brew install ollama
#   Linux:    curl -fsSL https://ollama.ai/install.sh | sh
#
# Start Ollama server:
#   ollama serve
#
# Pull models (pick ones you want):
#   ollama pull llama3.2           # Meta's Llama 3.2 (3B) - fast
#   ollama pull llama3.2:1b        # Llama 3.2 1B - very fast, small
#   ollama pull llama3.1:8b        # Llama 3.1 8B - good quality
#   ollama pull llama3.1:70b       # Llama 3.1 70B - best quality
#   ollama pull mistral            # Mistral 7B - excellent for writing
#   ollama pull mistral-nemo       # Mistral Nemo 12B - better writing
#   ollama pull mixtral            # Mixtral 8x7B - very capable
#   ollama pull phi4               # Microsoft Phi-4 14B
#   ollama pull phi3               # Microsoft Phi-3 Mini
#   ollama pull gemma2             # Google Gemma 2 9B
#   ollama pull gemma2:27b         # Google Gemma 2 27B
#   ollama pull qwen2.5            # Alibaba Qwen 2.5 7B
#   ollama pull qwen2.5:14b        # Alibaba Qwen 2.5 14B
#   ollama pull qwen2.5:72b        # Alibaba Qwen 2.5 72B - huge
#   ollama pull deepseek-r1        # DeepSeek R1 reasoning model
#   ollama pull deepseek-r1:7b     # DeepSeek R1 7B - fast
#   ollama pull neural-chat        # Intel Neural Chat
#   ollama pull orca-mini          # Orca Mini - very small
#   ollama pull vicuna             # Vicuna 7B
#   ollama pull codellama          # Code-focused Llama
#   ollama pull solar              # Solar 10.7B
#   ollama pull openchat           # OpenChat 3.5
#
# List installed models:
#   ollama list
#
# Check if running:
#   curl http://localhost:11434/api/tags
"""


def get_ollama_models(host: str = "localhost:11434") -> list[str]:
    """Fetch available local Ollama models"""
    try:
        url = f"http://{host}/api/tags"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception as e:
        logger.warning(f"Ollama not reachable at {host}: {e}")
    return []


def check_ollama_running(host: str = "localhost:11434") -> bool:
    try:
        r = requests.get(f"http://{host}/", timeout=3)
        return r.status_code == 200
    except:
        return False


# ─────────────────────── EMAIL FINDER ───────────────────────────────

class EmailFinder:
    COMMON_PATTERNS = [
        "info@{domain}", "contact@{domain}", "hello@{domain}",
        "admin@{domain}", "office@{domain}", "team@{domain}",
    ]

    def __init__(self, hunter_api_key: str = ""):
        self.hunter_api_key = hunter_api_key

    def find_email(self, lead) -> str:
        if lead.email:
            return lead.email
        if self.hunter_api_key and lead.website:
            email = self._hunter_lookup(lead.website)
            if email:
                lead.email = email
                return email
        return ""

    def _hunter_lookup(self, website: str) -> str:
        try:
            domain = website.replace("https://", "").replace("http://", "").split("/")[0]
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.hunter_api_key}&limit=1"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            emails = data.get("data", {}).get("emails", [])
            if emails:
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


# ─────────────────────── AI PERSONALIZER ────────────────────────────

class AIPersonalizer:
    """
    Multi-provider AI email generator.
    Supports Claude, OpenAI GPT, Google Gemini, Ollama local models.
    """

    def __init__(self,
                 provider: str = "Claude (Anthropic)",
                 model: str = "claude-sonnet-4-5",
                 api_key: str = "",
                 ollama_host: str = "localhost:11434",
                 your_name: str = "Mordecai",
                 your_website: str = "mordecai.web.app",
                 your_email: str = "Mordecai.a.d@gmail.com",
                 service_description: str = "",
                 email_template: str = "",
                 tone: str = "professional"):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.ollama_host = ollama_host
        self.your_name = your_name
        self.your_website = your_website
        self.your_email = your_email
        self.service_description = service_description or (
            "I build AI chatbots and RAG systems that help businesses automate "
            "customer support, handle FAQs, and save staff time."
        )
        self.email_template = email_template
        self.tone = tone  # professional / casual / aggressive / friendly

    def _build_system_prompt(self) -> str:
        tone_instructions = {
            "professional": "Formal, confident, business-to-business tone. Respect the reader's time.",
            "casual": "Conversational and warm. Sound like a real person, not a salesperson.",
            "aggressive": "Direct and bold. Create urgency. Don't be afraid to be blunt about value.",
            "friendly": "Upbeat, enthusiastic, personable. Build rapport first.",
        }
        tone_desc = tone_instructions.get(self.tone, tone_instructions["professional"])

        template_instruction = ""
        if self.email_template:
            template_instruction = f"""
Use this template as a structural guide but personalize it for the specific business:
---
{self.email_template}
---"""

        return f"""You are the world's best cold email copywriter. You write emails that get replies.

SENDER INFO:
- Name: {self.your_name}
- Website: {self.your_website}
- Email: {self.your_email}
- Service: {self.service_description}

TONE: {tone_desc}

RULES (non-negotiable):
1. NEVER open with "I hope this email finds you well" or any variant
2. First sentence must reference something SPECIFIC about this business (name, location, category, size)
3. Focus on ONE pain point, not a list of features
4. Under 160 words total - shorter is better
5. End with ONE soft CTA (10-minute call, quick question, or yes/no question)
6. Sound human - no buzzwords like "leverage", "synergize", "holistic solution"
7. Output format: Subject: [subject]\n\n[email body only, no extra labels]
{template_instruction}"""

    def _build_user_prompt(self, lead) -> str:
        return f"""Write a cold email for this business:

Business: {lead.name}
Type: {lead.category or "business"}
Location: {lead.address}
Reviews: {lead.review_count} ({lead.rating}★)
Has FAQ page: {lead.faq_page}
Has chatbot already: {lead.has_chatbot}
Tech stack: {", ".join(lead.tech_stack) or "unknown"}
Website: {lead.website or "unknown"}

Write the email now."""

    def generate_email(self, lead) -> str:
        """Route to the correct AI provider"""
        provider = self.provider

        if provider == "Claude (Anthropic)":
            return self._call_claude(lead)
        elif provider == "ChatGPT (OpenAI)":
            return self._call_openai(lead)
        elif provider == "Gemini (Google)":
            return self._call_gemini(lead)
        elif provider == "Ollama (Local)":
            return self._call_ollama(lead)
        else:
            return self._template_fallback(lead)

    def _call_claude(self, lead) -> str:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            msg = client.messages.create(
                model=self.model,
                max_tokens=500,
                system=self._build_system_prompt(),
                messages=[{"role": "user", "content": self._build_user_prompt(lead)}]
            )
            return msg.content[0].text.strip()
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return self._template_fallback(lead)

    def _call_openai(self, lead) -> str:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            resp = client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": self._build_user_prompt(lead)},
                ]
            )
            return resp.choices[0].message.content.strip()
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
            return self._template_fallback(lead)
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return self._template_fallback(lead)

    def _call_gemini(self, lead) -> str:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": self.api_key}
            body = {
                "contents": [{
                    "parts": [{
                        "text": self._build_system_prompt() + "\n\n" + self._build_user_prompt(lead)
                    }]
                }],
                "generationConfig": {
                    "maxOutputTokens": 500,
                    "temperature": 0.7,
                }
            }
            resp = requests.post(url, json=body, headers=headers, params=params, timeout=30)
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return self._template_fallback(lead)

    def _call_ollama(self, lead) -> str:
        try:
            url = f"http://{self.ollama_host}/api/generate"
            prompt = self._build_system_prompt() + "\n\n" + self._build_user_prompt(lead)
            body = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 500,
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }
            resp = requests.post(url, json=body, timeout=120)
            data = resp.json()
            return data.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            logger.error(f"Ollama not running at {self.ollama_host}. Start with: ollama serve")
            return self._template_fallback(lead)
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return self._template_fallback(lead)

    def test_connection(self) -> tuple[bool, str]:
        """Test the AI connection with a simple prompt"""
        try:
            class FakeLead:
                name = "Test Business"
                category = "law firm"
                address = "New York, NY"
                review_count = 45
                rating = 4.2
                faq_page = True
                has_chatbot = False
                tech_stack = ["WordPress"]
                website = "testbusiness.com"

            result = self.generate_email(FakeLead())
            if result and len(result) > 50:
                return True, f"✅ Connected! Sample output:\n\n{result[:200]}..."
            else:
                return False, "❌ Got empty response from AI"
        except Exception as e:
            return False, f"❌ Connection failed: {e}"

    def _template_fallback(self, lead) -> str:
        subject = f"Quick question about {lead.name}"
        body = f"""Hi,

I came across {lead.name} while looking for {lead.category or "businesses"} in {lead.address}.

I build AI assistants that answer your customer questions 24/7, trained specifically on your business — your services, pricing, and policies. No generic chatbot.

A client of mine cut their response time from hours to instant after we set one up.

Would a 10-minute call make sense this week?

{self.your_name}
{self.your_website}
{self.your_email}"""
        return f"Subject: {subject}\n\n{body}"
