"""
LeadHunter Pro - Main UI Application
Built with CustomTkinter for a modern, professional interface
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Set theme before anything else
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color palette
COLORS = {
    "bg_dark": "#0a0a14",
    "bg_card": "#12121f",
    "bg_input": "#1a1a2e",
    "accent": "#7c3aed",
    "accent_light": "#a855f7",
    "accent_green": "#10b981",
    "accent_red": "#ef4444",
    "accent_yellow": "#f59e0b",
    "text": "#e2e8f0",
    "text_muted": "#64748b",
    "border": "#2d2d44",
    "success": "#065f46",
    "warning": "#78350f",
    "error": "#7f1d1d",
}

# Preset business types
BUSINESS_TYPES = [
    "law firm", "real estate agency", "dental clinic", "accounting firm",
    "insurance agency", "medical clinic", "veterinary clinic", "physical therapy",
    "financial advisor", "mortgage broker", "HVAC company", "plumbing company",
    "roofing contractor", "landscaping company", "auto dealership", "car dealership",
    "restaurant", "hotel", "gym", "spa", "salon", "marketing agency",
    "IT consulting", "recruitment agency", "property management",
]

# Preset cities
CITIES_PRESETS = {
    "\U0001f1fa\U0001f1f8 US - Major": ["Chicago, IL", "New York, NY", "Los Angeles, CA", "Houston, TX",
                        "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "Dallas, TX",
                        "Austin, TX", "San Diego, CA"],
    "\U0001f1ec\U0001f1e7 UK - Major": ["London, UK", "Manchester, UK", "Birmingham, UK", "Leeds, UK",
                        "Glasgow, UK", "Liverpool, UK", "Bristol, UK", "Sheffield, UK"],
    "\U0001f1e8\U0001f1e6 Canada": ["Toronto, Canada", "Vancouver, Canada", "Calgary, Canada",
                   "Montreal, Canada", "Ottawa, Canada"],
    "\U0001f1e6\U0001f1fa Australia": ["Sydney, Australia", "Melbourne, Australia", "Brisbane, Australia",
                       "Perth, Australia"],
    "\U0001f1e9\U0001f1ea Germany": ["Berlin, Germany", "Munich, Germany", "Hamburg, Germany",
                    "Frankfurt, Germany", "Cologne, Germany"],
}

CONFIG_FILE = Path("data/config.json")


class LeadHunterApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("LeadHunter Pro \u2014 AI-Powered Lead Generation")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)

        self.leads = []
        self.scraper_thread = None
        self.sender_thread = None
        self._scraper_engine = None
        self._stop_send = False
        self.config = self._load_config()

        # Setup logging to UI
        self._setup_logging()

        # Build UI
        self._build_ui()

        # Restore config values to UI
        self._restore_config()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self._save_config()
        self.root.destroy()

    # ─────────────────────────── CONFIG ────────────────────────────

    def _load_config(self) -> dict:
        CONFIG_FILE.parent.mkdir(exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except:
                pass
        return {}

    def _save_config(self):
        try:
            cfg = {
                # API Keys & Credentials
                "anthropic_key": self.var_anthropic_key.get(),
                "openai_key": self.var_openai_key.get(),
                "gemini_key": self.var_gemini_key.get(),
                "hunter_key": self.var_hunter_key.get(),
                "ollama_host": self.var_ollama_host.get(),
                "gmail_address": self.var_gmail.get(),
                "gmail_password": self.var_gmail_pass.get(),
                # Identity
                "your_name": self.var_your_name.get(),
                "your_website": self.var_your_website.get(),
                "your_email_sig": self.var_your_email_sig.get(),
                "service_description": self.var_service_desc.get("1.0", "end-1c"),
                "email_template": self.var_email_template.get("1.0", "end-1c"),
                # Scrape targets
                "business_type": self.var_business_type.get(),
                "custom_cities": self.var_custom_cities.get("1.0", "end-1c"),
                # Scraper settings
                "max_per_city": self.var_max_per_city.get(),
                "min_reviews": self.var_min_reviews.get(),
                "max_reviews": self.var_max_reviews.get(),
                "min_delay": self.var_min_delay.get(),
                "max_delay": self.var_max_delay.get(),
                "headless": self.var_headless.get(),
                "skip_with_chatbot": self.var_skip_chatbot.get(),
                "require_email": self.var_require_email.get(),
                "min_score": self.var_min_score.get(),
                # Outreach settings
                "ai_provider": self.var_ai_provider.get(),
                "ai_model": self.var_ai_model.get(),
                "ai_tone": self.var_ai_tone.get(),
                "daily_email_limit": self.var_daily_limit.get(),
                "email_min_delay": self.var_email_min_delay.get(),
                "email_max_delay": self.var_email_max_delay.get(),
            }
            CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
        except Exception as e:
            print(f"Config save error: {e}")

    def _restore_config(self):
        cfg = self.config
        # API Keys & Credentials
        self._set_var(self.var_anthropic_key, cfg.get("anthropic_key", ""))
        self._set_var(self.var_openai_key, cfg.get("openai_key", ""))
        self._set_var(self.var_gemini_key, cfg.get("gemini_key", ""))
        self._set_var(self.var_hunter_key, cfg.get("hunter_key", ""))
        self._set_var(self.var_ollama_host, cfg.get("ollama_host", "localhost:11434"))
        self._set_var(self.var_gmail, cfg.get("gmail_address", ""))
        self._set_var(self.var_gmail_pass, cfg.get("gmail_password", ""))
        # Identity
        self._set_var(self.var_your_name, cfg.get("your_name", ""))
        self._set_var(self.var_your_website, cfg.get("your_website", ""))
        self._set_var(self.var_your_email_sig, cfg.get("your_email_sig", ""))
        self._set_textbox(self.var_service_desc, cfg.get("service_description", ""))
        self._set_textbox(self.var_email_template, cfg.get("email_template", ""))
        # Scrape targets
        if cfg.get("business_type"):
            self.var_business_type.set(cfg["business_type"])
        self._set_textbox(self.var_custom_cities, cfg.get("custom_cities", ""))
        # Scraper settings
        self._set_slider(self.var_max_per_city, cfg.get("max_per_city", 20))
        self._set_slider(self.var_min_reviews, cfg.get("min_reviews", 0))
        self._set_slider(self.var_max_reviews, cfg.get("max_reviews", 300))
        self._set_slider(self.var_min_delay, cfg.get("min_delay", 1.5))
        self._set_slider(self.var_max_delay, cfg.get("max_delay", 4.0))
        if "headless" in cfg:
            self.var_headless.set(cfg["headless"])
        if "skip_with_chatbot" in cfg:
            self.var_skip_chatbot.set(cfg["skip_with_chatbot"])
        if "require_email" in cfg:
            self.var_require_email.set(cfg["require_email"])
        self._set_slider(self.var_min_score, cfg.get("min_score", 40))
        # Outreach settings
        if cfg.get("ai_provider"):
            self.var_ai_provider.set(cfg["ai_provider"])
            self._on_provider_change(cfg["ai_provider"])
        if cfg.get("ai_model"):
            self.var_ai_model.set(cfg["ai_model"])
        if cfg.get("ai_tone"):
            self.var_ai_tone.set(cfg["ai_tone"])
        self._set_slider(self.var_daily_limit, cfg.get("daily_email_limit", 30))
        self._set_slider(self.var_email_min_delay, cfg.get("email_min_delay", 60))
        self._set_slider(self.var_email_max_delay, cfg.get("email_max_delay", 120))

    def _set_var(self, var, value):
        try:
            var.set(value)
        except:
            pass

    def _set_textbox(self, widget, value):
        try:
            widget.delete("1.0", "end")
            widget.insert("1.0", value)
        except:
            pass

    def _set_slider(self, var, value):
        try:
            var.set(value)
        except:
            pass

    # ─────────────────────────── LOGGING ───────────────────────────

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def _log(self, msg: str, level: str = "info"):
        """Write to the log panel in the UI"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            icons = {"info": "\u2139\ufe0f", "success": "\u2705", "warning": "\u26a0\ufe0f", "error": "\u274c"}
            icon = icons.get(level, "\u2022")
            formatted = f"[{timestamp}] {icon} {msg}\n"

            self.log_box.configure(state="normal")
            self.log_box.insert("end", formatted)
            self.log_box.configure(state="disabled")
            self.log_box.see("end")
        except:
            pass

    # ─────────────────────────── UI BUILD ──────────────────────────

    def _build_ui(self):
        # Main layout: sidebar + content
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_content()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self.root, width=220, fg_color="#0d0d1a", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=(25, 5), padx=15, fill="x")

        ctk.CTkLabel(logo_frame, text="\u26a1 LeadHunter", font=("Georgia", 20, "bold"),
                     text_color="#a855f7").pack(anchor="w")
        ctk.CTkLabel(logo_frame, text="Pro Edition", font=("Georgia", 11),
                     text_color="#475569").pack(anchor="w")

        ctk.CTkFrame(sidebar, height=1, fg_color="#2d2d44").pack(fill="x", padx=15, pady=15)

        # Nav buttons
        self.nav_buttons = {}
        nav_items = [
            ("\U0001f3af  Scrape Targets", "scrape"),
            ("\u2699\ufe0f  Scraper Settings", "settings"),
            ("\U0001f4e7  Outreach", "outreach"),
            ("\U0001f4ca  Leads Table", "leads"),
            ("\U0001f4dd  Activity Log", "log"),
            ("\U0001f511  API Keys", "keys"),
        ]

        for label, key in nav_items:
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w",
                font=("Consolas", 13),
                fg_color="transparent",
                hover_color="#1e1e35",
                text_color="#94a3b8",
                height=42,
                corner_radius=8,
                command=lambda k=key: self._show_panel(k)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[key] = btn

        # Stats at bottom
        ctk.CTkFrame(sidebar, height=1, fg_color="#2d2d44").pack(fill="x", padx=15, pady=15)
        self.lbl_stats = ctk.CTkLabel(sidebar,
                                      text="0 leads found\n0 emails sent",
                                      font=("Consolas", 11),
                                      text_color="#475569",
                                      justify="left")
        self.lbl_stats.pack(padx=15, anchor="w")

        # Version
        ctk.CTkLabel(sidebar, text="v1.1 | mordecai.web.app",
                     font=("Consolas", 10), text_color="#334155").pack(
            side="bottom", pady=10)

    def _build_main_content(self):
        self.content_frame = ctk.CTkFrame(self.root, fg_color="#0f0f1a", corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # All panels (only one visible at a time)
        self.panels = {}
        self.panels["scrape"] = self._build_scrape_panel()
        self.panels["settings"] = self._build_settings_panel()
        self.panels["outreach"] = self._build_outreach_panel()
        self.panels["leads"] = self._build_leads_panel()
        self.panels["log"] = self._build_log_panel()
        self.panels["keys"] = self._build_keys_panel()

        self._show_panel("scrape")

    def _show_panel(self, key: str):
        for k, panel in self.panels.items():
            panel.grid_remove()
        self.panels[key].grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Update nav button states
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color="#1e1e35", text_color="#a855f7")
            else:
                btn.configure(fg_color="transparent", text_color="#94a3b8")

    def _make_panel(self) -> ctk.CTkScrollableFrame:
        panel = ctk.CTkScrollableFrame(
            self.content_frame, fg_color="#0f0f1a",
            scrollbar_button_color="#2d2d44"
        )
        return panel

    def _section_header(self, parent, title: str, subtitle: str = ""):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=30, pady=(25, 5))
        ctk.CTkLabel(frame, text=title, font=("Georgia", 22, "bold"),
                     text_color="#e2e8f0").pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(frame, text=subtitle, font=("Consolas", 12),
                         text_color="#64748b").pack(anchor="w", pady=(2, 0))

    def _card(self, parent, **kwargs) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color="#12121f", corner_radius=12,
                            border_width=1, border_color="#2d2d44", **kwargs)
        return card

    def _label(self, parent, text, font_size=12, bold=False, color=None, **kwargs):
        font = ("Consolas", font_size, "bold" if bold else "normal")
        color = color or "#94a3b8"
        return ctk.CTkLabel(parent, text=text, font=font, text_color=color, **kwargs)

    def _entry(self, parent, var, placeholder="", show="", width=None, **kwargs):
        args = dict(textvariable=var, placeholder_text=placeholder,
                    fg_color="#1a1a2e", border_color="#374151",
                    text_color="#e2e8f0", placeholder_text_color="#4b5563",
                    font=("Consolas", 12))
        if show:
            args["show"] = show
        if width:
            args["width"] = width
        return ctk.CTkEntry(parent, **args, **kwargs)

    def _slider_row(self, parent, label, var, from_, to, step=1, fmt="{:.0f}"):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=4)

        lbl_name = self._label(row, label, 12)
        lbl_name.pack(side="left")

        lbl_val = self._label(row, fmt.format(var.get()), 12, color="#a855f7")
        lbl_val.pack(side="right")

        def update_label(val):
            lbl_val.configure(text=fmt.format(float(val)))

        slider = ctk.CTkSlider(row, variable=var, from_=from_, to=to,
                               number_of_steps=int((to - from_) / step),
                               button_color="#7c3aed", button_hover_color="#a855f7",
                               progress_color="#4c1d95", fg_color="#374151",
                               command=update_label, width=160)
        slider.pack(side="right", padx=(10, 5))
        return slider

    # ─────────────────────────── PANELS ────────────────────────────

    def _build_scrape_panel(self) -> ctk.CTkScrollableFrame:
        """Scrape Targets - focused on WHAT to scrape and WHERE"""
        panel = self._make_panel()

        self._section_header(panel, "\U0001f3af Target Configuration",
                             "Define what businesses to hunt and where")

        # ── Business Type card ──
        card = self._card(panel)
        card.pack(fill="x", padx=30, pady=10)
        self._label(card, "BUSINESS TYPE", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))

        self.var_business_type = tk.StringVar(value="law firm")
        type_menu = ctk.CTkComboBox(card, variable=self.var_business_type,
                                    values=BUSINESS_TYPES,
                                    fg_color="#1a1a2e", button_color="#7c3aed",
                                    button_hover_color="#a855f7",
                                    border_color="#374151",
                                    text_color="#e2e8f0", font=("Consolas", 13),
                                    width=400)
        type_menu.pack(anchor="w", padx=15, pady=(0, 12))

        self._label(card, "Or type a custom business type in the box above",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 12))

        # ── Cities card ──
        card2 = self._card(panel)
        card2.pack(fill="x", padx=30, pady=10)

        # Header row with stats
        hdr = ctk.CTkFrame(card2, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(12, 4))
        self._label(hdr, "TARGET CITIES \u2014 GLOBAL", 11, bold=True, color="#7c3aed").pack(side="left")
        from core.locations import get_stats
        stats = get_stats()
        self._label(hdr,
                    f"{stats['cities']} cities \u00b7 {stats['countries']} countries \u00b7 {stats['continents']} continents",
                    10, color="#475569").pack(side="right")

        # ── Search box ──
        search_row = ctk.CTkFrame(card2, fg_color="transparent")
        search_row.pack(fill="x", padx=15, pady=(0, 6))

        self.var_city_search = tk.StringVar()
        search_entry = ctk.CTkEntry(
            search_row, textvariable=self.var_city_search,
            placeholder_text="\U0001f50d  Search city or country (e.g. 'Nigeria', 'Chicago', 'Germany')...",
            fg_color="#1a1a2e", border_color="#7c3aed", border_width=1,
            text_color="#e2e8f0", placeholder_text_color="#4b5563",
            font=("Consolas", 12), height=36
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        add_search_btn = ctk.CTkButton(
            search_row, text="\u2795 Add Results",
            font=("Consolas", 11),
            fg_color="#7c3aed", hover_color="#5b21b6",
            height=36, corner_radius=8, width=110,
            command=self._add_search_results
        )
        add_search_btn.pack(side="left")

        self.var_city_search.trace_add("write", lambda *a: self._update_city_search())

        # Search results listbox
        self.city_search_frame = ctk.CTkFrame(card2, fg_color="#0d0d1a",
                                              border_width=1, border_color="#2d2d44",
                                              corner_radius=6)
        self.city_search_frame.pack(fill="x", padx=15, pady=(0, 6))

        self.city_listbox = tk.Listbox(
            self.city_search_frame,
            bg="#0d0d1a", fg="#94a3b8",
            selectbackground="#7c3aed", selectforeground="white",
            font=("Consolas", 11), height=6,
            borderwidth=0, highlightthickness=0,
            activestyle="none"
        )
        list_sb = tk.Scrollbar(self.city_search_frame, orient="vertical",
                               command=self.city_listbox.yview)
        self.city_listbox.configure(yscrollcommand=list_sb.set)
        list_sb.pack(side="right", fill="y")
        self.city_listbox.pack(fill="both", expand=True, padx=4, pady=4)
        self.city_listbox.bind("<Double-Button-1>", self._on_city_double_click)
        self.city_listbox.bind("<Return>", self._on_city_double_click)
        self.city_search_frame.pack_forget()  # Hidden until user types

        # ── Continent quick-add buttons ──
        self._label(card2, "Quick add by region:", 10, color="#475569").pack(
            anchor="w", padx=15, pady=(4, 4))

        from core.locations import LOCATIONS
        continent_rows = [
            list(LOCATIONS.keys())[:4],
            list(LOCATIONS.keys())[4:],
        ]
        for row_items in continent_rows:
            row_frame = ctk.CTkFrame(card2, fg_color="transparent")
            row_frame.pack(fill="x", padx=15, pady=2)
            for continent in row_items:
                short = continent.split(" ", 1)[1] if " " in continent else continent
                short = short.replace("Middle East & Central Asia", "Mid East")
                short = short.replace("Caribbean & Central America", "Caribbean")
                btn = ctk.CTkButton(
                    row_frame, text=continent.split()[0] + " " + short,
                    font=("Consolas", 10),
                    fg_color="#1a1a2e", hover_color="#2d2d44",
                    text_color="#94a3b8", border_width=1, border_color="#374151",
                    height=26, corner_radius=6,
                    command=lambda c=continent: self._add_continent(c)
                )
                btn.pack(side="left", padx=(0, 5))

        # Country dropdown row
        country_row = ctk.CTkFrame(card2, fg_color="transparent")
        country_row.pack(fill="x", padx=15, pady=(6, 4))

        self._label(country_row, "Add country:", 11).pack(side="left", padx=(0, 8))

        all_countries = []
        for continent, countries in LOCATIONS.items():
            all_countries.extend(list(countries.keys()))

        self.var_country_pick = tk.StringVar(value=all_countries[0])
        country_menu = ctk.CTkComboBox(
            country_row, variable=self.var_country_pick,
            values=all_countries,
            fg_color="#1a1a2e", button_color="#7c3aed",
            button_hover_color="#a855f7", border_color="#374151",
            text_color="#e2e8f0", font=("Consolas", 11), width=300
        )
        country_menu.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            country_row, text="\u2795 Add",
            font=("Consolas", 11),
            fg_color="#1a1a2e", hover_color="#2d2d44",
            text_color="#10b981", border_width=1, border_color="#374151",
            height=30, corner_radius=6, width=70,
            command=self._add_country
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            country_row, text="\U0001f30d Add ALL Cities",
            font=("Consolas", 11),
            fg_color="#1a1a2e", hover_color="#4c1d95",
            text_color="#a855f7", border_width=1, border_color="#374151",
            height=30, corner_radius=6,
            command=self._add_all_cities
        ).pack(side="left")

        # Action buttons row
        action_row = ctk.CTkFrame(card2, fg_color="transparent")
        action_row.pack(fill="x", padx=15, pady=(6, 6))

        ctk.CTkButton(
            action_row, text="\U0001f5d1 Clear All",
            font=("Consolas", 11),
            fg_color="#1a1a2e", hover_color="#7f1d1d",
            text_color="#ef4444", border_width=1, border_color="#374151",
            height=28, corner_radius=6,
            command=lambda: self._set_textbox(self.var_custom_cities, "")
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            action_row, text="\U0001f4cb Count Cities",
            font=("Consolas", 11),
            fg_color="#1a1a2e", hover_color="#2d2d44",
            text_color="#94a3b8", border_width=1, border_color="#374151",
            height=28, corner_radius=6,
            command=self._count_cities
        ).pack(side="left")

        self.lbl_city_count = self._label(action_row, "", 11, color="#a855f7")
        self.lbl_city_count.pack(side="left", padx=(10, 0))

        self._label(card2, "Cities queued (one per line \u2014 you can also type manually):",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(4, 2))

        self.var_custom_cities = ctk.CTkTextbox(
            card2, height=160, fg_color="#1a1a2e",
            text_color="#e2e8f0", font=("Consolas", 11),
            border_color="#374151", border_width=1
        )
        self.var_custom_cities.pack(fill="x", padx=15, pady=(0, 12))

        # ── Launch card ──
        launch_card = self._card(panel)
        launch_card.pack(fill="x", padx=30, pady=10)

        self.var_scrape_progress = tk.DoubleVar(value=0)
        self.progress_bar = ctk.CTkProgressBar(launch_card,
                                               variable=self.var_scrape_progress,
                                               progress_color="#7c3aed",
                                               fg_color="#1a1a2e")
        self.progress_bar.pack(fill="x", padx=15, pady=(15, 5))

        self.lbl_scrape_status = self._label(launch_card, "Ready to hunt leads",
                                             12, color="#64748b")
        self.lbl_scrape_status.pack(anchor="w", padx=15, pady=(0, 10))

        btn_row = ctk.CTkFrame(launch_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=15, pady=(0, 15))

        self.btn_start_scrape = ctk.CTkButton(
            btn_row, text="\U0001f680  START HUNTING",
            font=("Georgia", 14, "bold"),
            fg_color="#7c3aed", hover_color="#5b21b6",
            height=46, corner_radius=10,
            command=self._start_scrape
        )
        self.btn_start_scrape.pack(side="left", padx=(0, 10))

        self.btn_stop_scrape = ctk.CTkButton(
            btn_row, text="\u23f9 Stop",
            font=("Consolas", 13),
            fg_color="#1a1a2e", hover_color="#7f1d1d",
            text_color="#ef4444", border_width=1, border_color="#374151",
            height=46, corner_radius=10,
            command=self._stop_scrape
        )
        self.btn_stop_scrape.pack(side="left")

        export_btn = ctk.CTkButton(
            btn_row, text="\U0001f4be Export Leads",
            font=("Consolas", 13),
            fg_color="#1a1a2e", hover_color="#064e3b",
            text_color="#10b981", border_width=1, border_color="#374151",
            height=46, corner_radius=10,
            command=self._export_leads
        )
        export_btn.pack(side="right")

        return panel

    def _build_settings_panel(self) -> ctk.CTkScrollableFrame:
        """Scraper Settings - all scraping behavior, filters, and tuning"""
        panel = self._make_panel()
        self._section_header(panel, "\u2699\ufe0f Scraper Settings",
                             "Fine-tune scraping behavior, filters, and anti-detection")

        # ── Volume Settings ──
        card_vol = self._card(panel)
        card_vol.pack(fill="x", padx=30, pady=10)
        self._label(card_vol, "VOLUME SETTINGS", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(card_vol, "Control how many results to scrape per city",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 8))

        self.var_max_per_city = tk.DoubleVar(value=20)
        self._slider_row(card_vol, "Max results per city", self.var_max_per_city, 5, 100, 5)
        ctk.CTkFrame(card_vol, height=12, fg_color="transparent").pack()

        # ── Review Filters ──
        card_rev = self._card(panel)
        card_rev.pack(fill="x", padx=30, pady=10)
        self._label(card_rev, "REVIEW FILTERS", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(card_rev, "Filter businesses by Google review count",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 8))

        self.var_min_reviews = tk.DoubleVar(value=0)
        self.var_max_reviews = tk.DoubleVar(value=300)
        self._slider_row(card_rev, "Min review count", self.var_min_reviews, 0, 100, 1)
        self._slider_row(card_rev, "Max review count (bigger = too corporate)",
                         self.var_max_reviews, 50, 2000, 50)
        ctk.CTkFrame(card_rev, height=12, fg_color="transparent").pack()

        # ── Scraping Behavior ──
        card_behav = self._card(panel)
        card_behav.pack(fill="x", padx=30, pady=10)
        self._label(card_behav, "SCRAPING BEHAVIOR", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(card_behav, "Toggle scraping options and lead filters",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 8))

        toggle_frame = ctk.CTkFrame(card_behav, fg_color="transparent")
        toggle_frame.pack(fill="x", padx=15, pady=(0, 12))

        self.var_headless = tk.BooleanVar(value=True)
        self.var_skip_chatbot = tk.BooleanVar(value=True)
        self.var_require_email = tk.BooleanVar(value=False)

        ctk.CTkSwitch(toggle_frame, text="Run browser headless (invisible)",
                      variable=self.var_headless,
                      font=("Consolas", 12), text_color="#94a3b8",
                      button_color="#7c3aed").pack(anchor="w", pady=3)
        ctk.CTkSwitch(toggle_frame, text="Skip businesses that already have a chatbot",
                      variable=self.var_skip_chatbot,
                      font=("Consolas", 12), text_color="#94a3b8",
                      button_color="#7c3aed").pack(anchor="w", pady=3)
        ctk.CTkSwitch(toggle_frame, text="Only keep leads with found email",
                      variable=self.var_require_email,
                      font=("Consolas", 12), text_color="#94a3b8",
                      button_color="#7c3aed").pack(anchor="w", pady=3)

        # ── Delays ──
        card_delay = self._card(panel)
        card_delay.pack(fill="x", padx=30, pady=10)
        self._label(card_delay, "ANTI-DETECTION DELAYS", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(card_delay, "Longer delays = lower detection risk. Randomized between min/max.",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 8))

        self.var_min_delay = tk.DoubleVar(value=1.5)
        self.var_max_delay = tk.DoubleVar(value=4.0)
        self._slider_row(card_delay, "Min delay between pages", self.var_min_delay, 0.5, 10, 0.5, "{:.1f}s")
        self._slider_row(card_delay, "Max delay between pages", self.var_max_delay, 1.0, 15, 0.5, "{:.1f}s")
        ctk.CTkFrame(card_delay, height=12, fg_color="transparent").pack()

        # ── Lead Scoring ──
        card_score = self._card(panel)
        card_score.pack(fill="x", padx=30, pady=10)
        self._label(card_score, "LEAD QUALITY FILTER", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(card_score, "Leads below minimum score are still saved but flagged red",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 8))

        self.var_min_score = tk.DoubleVar(value=40)
        self._slider_row(card_score, "Minimum lead score to email (0-100)", self.var_min_score, 0, 100, 5)
        ctk.CTkFrame(card_score, height=12, fg_color="transparent").pack()

        # ── Score explanation ──
        card_explain = self._card(panel)
        card_explain.pack(fill="x", padx=30, pady=10)
        self._label(card_explain, "HOW SCORING WORKS", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))

        score_items = [
            ("\u2705 Has email found", "+20"),
            ("\u2705 No existing chatbot", "+15"),
            ("\u2705 Has FAQ page (needs bot)", "+10"),
            ("\u2705 10\u2013200 reviews (right size)", "+10"),
            ("\u2705 Rating \u2265 4.0 (has budget)", "+5"),
            ("\u2705 Has website", "+5"),
            ("\u2705 WordPress (easy install)", "+5"),
            ("\u274c Already has chatbot", "-20"),
            ("\u274c 500+ reviews (too big)", "-15"),
        ]
        for item, pts in score_items:
            row = ctk.CTkFrame(card_explain, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=1)
            self._label(row, item, 11).pack(side="left")
            color = "#10b981" if pts.startswith("+") else "#ef4444"
            self._label(row, pts, 11, bold=True, color=color).pack(side="right")

        ctk.CTkFrame(card_explain, height=12, fg_color="transparent").pack()
        return panel

    def _build_outreach_panel(self) -> ctk.CTkScrollableFrame:
        """Outreach - identity, AI email writing, and sending"""
        panel = self._make_panel()
        self._section_header(panel, "\U0001f4e7 Outreach Configuration",
                             "AI email writing, identity, and sending controls")

        # ── Identity card ──
        card = self._card(panel)
        card.pack(fill="x", padx=30, pady=10)
        self._label(card, "YOUR IDENTITY", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))

        fields = ctk.CTkFrame(card, fg_color="transparent")
        fields.pack(fill="x", padx=15, pady=(0, 4))
        fields.grid_columnconfigure((0, 1), weight=1)

        self.var_your_name = tk.StringVar()
        self.var_your_website = tk.StringVar()
        self.var_your_email_sig = tk.StringVar()

        self._label(fields, "Your Name", 11).grid(row=0, column=0, sticky="w", pady=3)
        self._entry(fields, self.var_your_name, "Your Name").grid(
            row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))
        self._label(fields, "Your Website", 11).grid(row=0, column=1, sticky="w", pady=3)
        self._entry(fields, self.var_your_website, "yoursite.com").grid(
            row=1, column=1, sticky="ew", pady=(0, 8))
        self._label(fields, "Email Signature", 11).grid(row=2, column=0, sticky="w", pady=3)
        self._entry(fields, self.var_your_email_sig, "your@email.com").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        self._label(card, "What you offer (AI uses this to write emails)", 11,
                    color="#64748b").pack(anchor="w", padx=15, pady=(4, 4))
        self.var_service_desc = ctk.CTkTextbox(
            card, height=80, fg_color="#1a1a2e", text_color="#e2e8f0",
            font=("Consolas", 12), border_color="#374151", border_width=1)
        self.var_service_desc.pack(fill="x", padx=15, pady=(0, 6))

        self._label(card, "Custom email template (optional \u2014 AI adapts this)", 11,
                    color="#64748b").pack(anchor="w", padx=15, pady=(8, 4))
        self.var_email_template = ctk.CTkTextbox(
            card, height=150, fg_color="#1a1a2e", text_color="#e2e8f0",
            font=("Consolas", 12), border_color="#374151", border_width=1)
        self.var_email_template.pack(fill="x", padx=15, pady=(0, 12))

        # ── AI Provider card ──
        ai_card = self._card(panel)
        ai_card.pack(fill="x", padx=30, pady=10)
        self._label(ai_card, "AI EMAIL WRITER", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(ai_card,
            "Choose which AI writes your cold emails. API keys are managed in the API Keys tab.",
            10, color="#475569").pack(anchor="w", padx=15, pady=(0, 10))

        from core.outreach import AI_PROVIDERS

        # Provider selector
        prov_row = ctk.CTkFrame(ai_card, fg_color="transparent")
        prov_row.pack(fill="x", padx=15, pady=(0, 8))
        self._label(prov_row, "Provider:", 12).pack(side="left", padx=(0, 10))

        self.var_ai_provider = tk.StringVar(value="Claude (Anthropic)")
        prov_menu = ctk.CTkComboBox(
            prov_row, variable=self.var_ai_provider,
            values=list(AI_PROVIDERS.keys()),
            fg_color="#1a1a2e", button_color="#7c3aed",
            button_hover_color="#a855f7", border_color="#374151",
            text_color="#e2e8f0", font=("Consolas", 13), width=260,
            command=self._on_provider_change
        )
        prov_menu.pack(side="left")

        # Model selector
        model_row = ctk.CTkFrame(ai_card, fg_color="transparent")
        model_row.pack(fill="x", padx=15, pady=(0, 8))
        self._label(model_row, "Model:", 12).pack(side="left", padx=(0, 10))

        self.var_ai_model = tk.StringVar(value="claude-sonnet-4-5")
        self.ai_model_menu = ctk.CTkComboBox(
            model_row, variable=self.var_ai_model,
            values=AI_PROVIDERS["Claude (Anthropic)"]["models"],
            fg_color="#1a1a2e", button_color="#7c3aed",
            button_hover_color="#a855f7", border_color="#374151",
            text_color="#e2e8f0", font=("Consolas", 13), width=340
        )
        self.ai_model_menu.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            model_row, text="\U0001f504 Refresh Ollama",
            font=("Consolas", 11), height=30, width=130,
            fg_color="#1a1a2e", hover_color="#2d2d44",
            text_color="#94a3b8", border_width=1, border_color="#374151",
            command=self._refresh_ollama_models
        ).pack(side="left")

        # Tone selector
        tone_row = ctk.CTkFrame(ai_card, fg_color="transparent")
        tone_row.pack(fill="x", padx=15, pady=(0, 8))
        self._label(tone_row, "Email Tone:", 12).pack(side="left", padx=(0, 10))

        self.var_ai_tone = tk.StringVar(value="professional")
        for tone_val, tone_label in [
            ("professional", "\U0001f4bc Professional"),
            ("casual", "\U0001f60a Casual"),
            ("aggressive", "\u26a1 Aggressive"),
            ("friendly", "\U0001f91d Friendly"),
        ]:
            ctk.CTkRadioButton(
                tone_row, text=tone_label, variable=self.var_ai_tone,
                value=tone_val, font=("Consolas", 11), text_color="#94a3b8",
                fg_color="#7c3aed", radiobutton_width=14, radiobutton_height=14,
            ).pack(side="left", padx=(0, 14))

        # Provider info hint
        self.lbl_provider_hint = self._label(ai_card, "", 10, color="#475569")
        self.lbl_provider_hint.pack(anchor="w", padx=15, pady=(0, 4))

        # Test AI button
        test_row = ctk.CTkFrame(ai_card, fg_color="transparent")
        test_row.pack(fill="x", padx=15, pady=(0, 12))
        ctk.CTkButton(
            test_row, text="\U0001f9ea Test AI Connection",
            font=("Consolas", 12), height=34, width=180,
            fg_color="#5b21b6", hover_color="#4c1d95",
            command=self._test_ai_connection
        ).pack(side="left")

        # ── Sending Throttle ──
        card_throttle = self._card(panel)
        card_throttle.pack(fill="x", padx=30, pady=10)
        self._label(card_throttle, "SENDING THROTTLE", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(card_throttle, "30\u201350/day is safe. Gmail hard limit is 500/day.",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 8))

        self.var_daily_limit = tk.DoubleVar(value=30)
        self.var_email_min_delay = tk.DoubleVar(value=60)
        self.var_email_max_delay = tk.DoubleVar(value=120)

        self._slider_row(card_throttle, "Daily send limit", self.var_daily_limit, 5, 100, 5)
        self._slider_row(card_throttle, "Min delay between emails (sec)",
                         self.var_email_min_delay, 20, 300, 10, "{:.0f}s")
        self._slider_row(card_throttle, "Max delay between emails (sec)",
                         self.var_email_max_delay, 30, 600, 10, "{:.0f}s")
        ctk.CTkFrame(card_throttle, height=12, fg_color="transparent").pack()

        # ── Generate & Send ──
        card_send = self._card(panel)
        card_send.pack(fill="x", padx=30, pady=10)
        self._label(card_send, "GENERATE & SEND", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))

        self.var_send_progress = tk.DoubleVar(value=0)
        self.send_progress_bar = ctk.CTkProgressBar(
            card_send, variable=self.var_send_progress,
            progress_color="#10b981", fg_color="#1a1a2e")
        self.send_progress_bar.pack(fill="x", padx=15, pady=(8, 4))

        self.lbl_send_status = self._label(card_send, "Ready \u2014 scrape leads first", 12, color="#64748b")
        self.lbl_send_status.pack(anchor="w", padx=15, pady=(0, 10))

        btn_row = ctk.CTkFrame(card_send, fg_color="transparent")
        btn_row.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            btn_row, text="\U0001f916 Generate AI Emails",
            font=("Georgia", 13, "bold"),
            fg_color="#5b21b6", hover_color="#4c1d95",
            height=44, corner_radius=10,
            command=self._generate_emails
        ).pack(side="left", padx=(0, 10))

        self.btn_start_send = ctk.CTkButton(
            btn_row, text="\U0001f4e4 Start Sending",
            font=("Georgia", 13, "bold"),
            fg_color="#065f46", hover_color="#047857", text_color="#34d399",
            height=44, corner_radius=10, command=self._start_send
        )
        self.btn_start_send.pack(side="left", padx=(0, 10))

        self.btn_stop_send = ctk.CTkButton(
            btn_row, text="\u23f9 Stop",
            font=("Consolas", 12),
            fg_color="#1a1a2e", hover_color="#7f1d1d",
            text_color="#ef4444", border_width=1, border_color="#374151",
            height=44, corner_radius=10, command=self._stop_send_fn
        )
        self.btn_stop_send.pack(side="left")

        return panel


    def _build_leads_panel(self) -> ctk.CTkFrame:
        # Non-scrollable panel for the table
        panel = ctk.CTkFrame(self.content_frame, fg_color="#0f0f1a", corner_radius=0)

        header_row = ctk.CTkFrame(panel, fg_color="transparent")
        header_row.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(header_row, text="\U0001f4ca Leads Table",
                     font=("Georgia", 22, "bold"), text_color="#e2e8f0").pack(side="left")

        # Toolbar
        toolbar = ctk.CTkFrame(header_row, fg_color="transparent")
        toolbar.pack(side="right")

        ctk.CTkButton(toolbar, text="\U0001f504 Refresh", font=("Consolas", 12),
                      fg_color="#1a1a2e", hover_color="#2d2d44", text_color="#94a3b8",
                      border_width=1, border_color="#374151", height=32,
                      command=self._refresh_leads_table).pack(side="left", padx=4)

        ctk.CTkButton(toolbar, text="\U0001f4cb Export CSV", font=("Consolas", 12),
                      fg_color="#1a1a2e", hover_color="#064e3b", text_color="#10b981",
                      border_width=1, border_color="#374151", height=32,
                      command=lambda: self._export_leads("csv")).pack(side="left", padx=4)

        ctk.CTkButton(toolbar, text="\U0001f4ca Export Excel", font=("Consolas", 12),
                      fg_color="#1a1a2e", hover_color="#064e3b", text_color="#10b981",
                      border_width=1, border_color="#374151", height=32,
                      command=lambda: self._export_leads("xlsx")).pack(side="left", padx=4)

        ctk.CTkButton(toolbar, text="\U0001f4be Export JSON", font=("Consolas", 12),
                      fg_color="#1a1a2e", hover_color="#064e3b", text_color="#10b981",
                      border_width=1, border_color="#374151", height=32,
                      command=lambda: self._export_leads("json")).pack(side="left", padx=4)

        ctk.CTkButton(toolbar, text="\U0001f4c2 Load JSON", font=("Consolas", 12),
                      fg_color="#1a1a2e", hover_color="#2d2d44", text_color="#94a3b8",
                      border_width=1, border_color="#374151", height=32,
                      command=self._load_leads).pack(side="left", padx=4)

        # Filter row
        filter_row = ctk.CTkFrame(panel, fg_color="#12121f", corner_radius=8)
        filter_row.pack(fill="x", padx=30, pady=(0, 10))

        self._label(filter_row, "Filter:", 12).pack(side="left", padx=(12, 8), pady=8)

        self.var_filter_status = tk.StringVar(value="all")
        for status in ["all", "new", "emailed", "replied", "converted"]:
            ctk.CTkRadioButton(
                filter_row, text=status, variable=self.var_filter_status,
                value=status, font=("Consolas", 11), text_color="#94a3b8",
                radiobutton_width=14, radiobutton_height=14,
                fg_color="#7c3aed",
                command=self._refresh_leads_table
            ).pack(side="left", padx=8, pady=8)

        self._label(filter_row, "Min score:", 12).pack(side="left", padx=(20, 4), pady=8)
        self.var_filter_score = tk.DoubleVar(value=0)
        ctk.CTkSlider(filter_row, variable=self.var_filter_score,
                      from_=0, to=100, width=100,
                      button_color="#7c3aed", command=lambda v: self._refresh_leads_table()
                      ).pack(side="left", pady=8)
        self.lbl_filter_score = self._label(filter_row, "0+", 11, color="#a855f7")
        self.lbl_filter_score.pack(side="left", padx=4)

        def update_score_label(v):
            self.lbl_filter_score.configure(text=f"{int(float(v))}+")
            self._refresh_leads_table()
        self.var_filter_score.trace_add("write", lambda *a: update_score_label(self.var_filter_score.get()))

        # Table using tk.Text for performance (scrollable)
        table_frame = ctk.CTkFrame(panel, fg_color="#0a0a14", corner_radius=0)
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Scrollbars
        vsb = tk.Scrollbar(table_frame, orient="vertical")
        hsb = tk.Scrollbar(table_frame, orient="horizontal")

        self.leads_text = tk.Text(
            table_frame, bg="#0a0a14", fg="#e2e8f0",
            font=("Consolas", 11), wrap="none",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set,
            state="disabled", selectbackground="#2d2d44",
            insertbackground="#7c3aed"
        )

        vsb.config(command=self.leads_text.yview)
        hsb.config(command=self.leads_text.xview)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.leads_text.pack(fill="both", expand=True)

        # Color tags
        self.leads_text.tag_configure("header", foreground="#a855f7", font=("Consolas", 11, "bold"))
        self.leads_text.tag_configure("high", foreground="#34d399")
        self.leads_text.tag_configure("mid", foreground="#fbbf24")
        self.leads_text.tag_configure("low", foreground="#f87171")
        self.leads_text.tag_configure("emailed", foreground="#60a5fa")
        self.leads_text.tag_configure("sep", foreground="#2d2d44")

        return panel

    def _build_log_panel(self) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(self.content_frame, fg_color="#0f0f1a", corner_radius=0)

        header_row = ctk.CTkFrame(panel, fg_color="transparent")
        header_row.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(header_row, text="\U0001f4dd Activity Log",
                     font=("Georgia", 22, "bold"), text_color="#e2e8f0").pack(side="left")

        ctk.CTkButton(header_row, text="\U0001f5d1 Clear Log", font=("Consolas", 12),
                      fg_color="#1a1a2e", hover_color="#7f1d1d", text_color="#ef4444",
                      border_width=1, border_color="#374151", height=32,
                      command=self._clear_log).pack(side="right")

        self.log_box = ctk.CTkTextbox(
            panel, fg_color="#0a0a14", text_color="#94a3b8",
            font=("Consolas", 11), wrap="word",
            scrollbar_button_color="#2d2d44", state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        return panel

    def _build_keys_panel(self) -> ctk.CTkScrollableFrame:
        """API Keys & Credentials - single source of truth for all keys"""
        panel = self._make_panel()
        self._section_header(panel, "\U0001f511 API Keys & Credentials",
                             "All keys and credentials in one place \u2014 saved locally to data/config.json")

        # ── AI Provider Keys ──
        ai_card = self._card(panel)
        ai_card.pack(fill="x", padx=30, pady=10)
        self._label(ai_card, "AI PROVIDER KEYS", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(ai_card, "Enter the API key for whichever AI provider you use",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 8))

        # Anthropic
        self.var_anthropic_key = tk.StringVar()
        self._label(ai_card, "Anthropic API Key (Claude)", 12, bold=True, color="#a855f7").pack(
            anchor="w", padx=15, pady=(8, 2))
        self._label(ai_card, "Get key: console.anthropic.com", 10, color="#475569").pack(
            anchor="w", padx=15, pady=(0, 4))
        key_row_ant = ctk.CTkFrame(ai_card, fg_color="transparent")
        key_row_ant.pack(fill="x", padx=15, pady=(0, 8))
        self._entry(key_row_ant, self.var_anthropic_key, "sk-ant-...", show="\u2022").pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(key_row_ant, text="\U0001f441", width=36, height=32,
                      fg_color="#1a1a2e", hover_color="#2d2d44", text_color="#94a3b8",
                      border_width=1, border_color="#374151",
                      command=lambda: self._toggle_key_visibility(key_row_ant)
                      ).pack(side="left")

        # OpenAI
        self.var_openai_key = tk.StringVar()
        self._label(ai_card, "OpenAI API Key (ChatGPT)", 12, bold=True, color="#a855f7").pack(
            anchor="w", padx=15, pady=(8, 2))
        self._label(ai_card, "Get key: platform.openai.com/api-keys", 10, color="#475569").pack(
            anchor="w", padx=15, pady=(0, 4))
        key_row_oai = ctk.CTkFrame(ai_card, fg_color="transparent")
        key_row_oai.pack(fill="x", padx=15, pady=(0, 8))
        self._entry(key_row_oai, self.var_openai_key, "sk-...", show="\u2022").pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(key_row_oai, text="\U0001f441", width=36, height=32,
                      fg_color="#1a1a2e", hover_color="#2d2d44", text_color="#94a3b8",
                      border_width=1, border_color="#374151",
                      command=lambda: self._toggle_key_visibility(key_row_oai)
                      ).pack(side="left")

        # Gemini
        self.var_gemini_key = tk.StringVar()
        self._label(ai_card, "Google Gemini API Key", 12, bold=True, color="#a855f7").pack(
            anchor="w", padx=15, pady=(8, 2))
        self._label(ai_card, "Get key: aistudio.google.com/app/apikey", 10, color="#475569").pack(
            anchor="w", padx=15, pady=(0, 4))
        key_row_gem = ctk.CTkFrame(ai_card, fg_color="transparent")
        key_row_gem.pack(fill="x", padx=15, pady=(0, 8))
        self._entry(key_row_gem, self.var_gemini_key, "AIza...", show="\u2022").pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(key_row_gem, text="\U0001f441", width=36, height=32,
                      fg_color="#1a1a2e", hover_color="#2d2d44", text_color="#94a3b8",
                      border_width=1, border_color="#374151",
                      command=lambda: self._toggle_key_visibility(key_row_gem)
                      ).pack(side="left")

        ctk.CTkFrame(ai_card, height=12, fg_color="transparent").pack()

        # ── Ollama ──
        ollama_card = self._card(panel)
        ollama_card.pack(fill="x", padx=30, pady=10)
        self._label(ollama_card, "OLLAMA (LOCAL AI)", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(ollama_card, "No API key needed \u2014 runs on your machine. Install: ollama.ai",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 8))

        ollama_row = ctk.CTkFrame(ollama_card, fg_color="transparent")
        ollama_row.pack(fill="x", padx=15, pady=(0, 4))
        self._label(ollama_row, "Host:", 11).pack(side="left", padx=(0, 8))
        self.var_ollama_host = tk.StringVar(value="localhost:11434")
        self._entry(ollama_row, self.var_ollama_host, "localhost:11434", width=220).pack(
            side="left", padx=(0, 8))
        self.lbl_ollama_status = self._label(ollama_row, "\u25cf not checked", 11, color="#475569")
        self.lbl_ollama_status.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            ollama_row, text="Check Ollama",
            font=("Consolas", 11), height=28, width=110,
            fg_color="#1a1a2e", hover_color="#2d2d44",
            text_color="#94a3b8", border_width=1, border_color="#374151",
            command=self._check_ollama
        ).pack(side="left")

        ctk.CTkFrame(ollama_card, height=12, fg_color="transparent").pack()

        # ── Hunter.io ──
        hunter_card = self._card(panel)
        hunter_card.pack(fill="x", padx=30, pady=10)
        self._label(hunter_card, "HUNTER.IO (OPTIONAL)", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(hunter_card, "Email finder service \u2014 finds emails by domain. Optional.",
                    10, color="#475569").pack(anchor="w", padx=15, pady=(0, 8))

        self.var_hunter_key = tk.StringVar()
        key_row_hunter = ctk.CTkFrame(hunter_card, fg_color="transparent")
        key_row_hunter.pack(fill="x", padx=15, pady=(0, 8))
        self._entry(key_row_hunter, self.var_hunter_key, "your-hunter-key", show="\u2022").pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(key_row_hunter, text="\U0001f441", width=36, height=32,
                      fg_color="#1a1a2e", hover_color="#2d2d44", text_color="#94a3b8",
                      border_width=1, border_color="#374151",
                      command=lambda: self._toggle_key_visibility(key_row_hunter)
                      ).pack(side="left")
        ctk.CTkFrame(hunter_card, height=12, fg_color="transparent").pack()

        # ── Gmail Credentials ──
        gmail_card = self._card(panel)
        gmail_card.pack(fill="x", padx=30, pady=10)
        self._label(gmail_card, "GMAIL SENDING CREDENTIALS", 11, bold=True, color="#7c3aed").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(gmail_card,
            "\u26a0\ufe0f Use a Gmail App Password (not your regular password).\n"
            "Enable 2FA first: myaccount.google.com \u2192 Security \u2192 App Passwords",
            11, color="#f59e0b").pack(anchor="w", padx=15, pady=(0, 8))

        g_fields = ctk.CTkFrame(gmail_card, fg_color="transparent")
        g_fields.pack(fill="x", padx=15, pady=(0, 8))
        g_fields.grid_columnconfigure((0, 1), weight=1)

        self.var_gmail = tk.StringVar()
        self.var_gmail_pass = tk.StringVar()

        self._label(g_fields, "Gmail Address", 11).grid(row=0, column=0, sticky="w")
        self._entry(g_fields, self.var_gmail, "you@gmail.com").grid(
            row=1, column=0, sticky="ew", padx=(0, 8), pady=(2, 8))
        self._label(g_fields, "App Password (16 chars)", 11).grid(row=0, column=1, sticky="w")
        self._entry(g_fields, self.var_gmail_pass, "xxxx xxxx xxxx xxxx",
                    show="\u2022").grid(row=1, column=1, sticky="ew", pady=(2, 8))

        ctk.CTkButton(
            gmail_card, text="\U0001f50c Test Gmail Connection",
            font=("Consolas", 12), fg_color="#1a1a2e", hover_color="#064e3b",
            text_color="#10b981", border_width=1, border_color="#374151",
            height=36, corner_radius=8, command=self._test_gmail
        ).pack(anchor="w", padx=15, pady=(0, 12))

        # ── Save button ──
        ctk.CTkButton(
            panel, text="\U0001f4be Save All Settings",
            font=("Georgia", 14, "bold"),
            fg_color="#7c3aed", hover_color="#5b21b6",
            height=46, corner_radius=10,
            command=lambda: (self._save_config(), self._log("All settings saved.", "success"))
        ).pack(padx=30, pady=15, anchor="w")

        # ── Security note ──
        note_card = self._card(panel)
        note_card.pack(fill="x", padx=30, pady=10)
        self._label(note_card, "\U0001f512 SECURITY NOTE", 11, bold=True, color="#f59e0b").pack(
            anchor="w", padx=15, pady=(12, 4))
        self._label(note_card,
                    "All credentials are stored locally in data/config.json on your machine.\n"
                    "This file is in .gitignore and will never be committed to version control.",
                    11, color="#64748b").pack(anchor="w", padx=15, pady=(0, 12))

        return panel

    # ─────────────────────────── ACTIONS ───────────────────────────

    def _toggle_key_visibility(self, row_frame):
        """Toggle show/hide for the entry widget in a key row"""
        for child in row_frame.winfo_children():
            if isinstance(child, ctk.CTkEntry):
                current = child.cget("show")
                child.configure(show="" if current else "\u2022")
                break

    def _add_cities(self, cities: list):
        current = self.var_custom_cities.get("1.0", "end-1c").strip()
        existing = set(c.strip() for c in current.split("\n") if c.strip())
        new_cities = [c for c in cities if c not in existing]
        combined = (current + "\n" + "\n".join(new_cities)).strip()
        self._set_textbox(self.var_custom_cities, combined)
        try:
            self._count_cities()
        except:
            pass

    def _add_continent(self, continent: str):
        from core.locations import get_continent_cities
        cities = get_continent_cities(continent)
        self._add_cities(cities)
        self._log(f"Added {len(cities)} cities from {continent}", "success")

    def _add_country(self):
        from core.locations import get_country_cities
        country = self.var_country_pick.get()
        cities = get_country_cities(country)
        if cities:
            self._add_cities(cities)
            self._log(f"Added {len(cities)} cities from {country}", "success")

    def _add_all_cities(self):
        from core.locations import get_all_cities
        if not messagebox.askyesno("Add ALL Cities",
            "This will add every city in the database (500+ cities across 100+ countries).\n\nProceed?"):
            return
        cities = get_all_cities()
        self._add_cities(cities)
        self._log(f"Added ALL {len(cities)} global cities!", "success")

    def _add_search_results(self):
        from core.locations import search_cities
        query = self.var_city_search.get().strip()
        if not query:
            return
        cities = search_cities(query)
        if cities:
            self._add_cities(cities)
            self._log(f"Added {len(cities)} cities matching '{query}'", "success")
        else:
            messagebox.showinfo("No Results", f"No cities found matching '{query}'")

    def _update_city_search(self):
        from core.locations import search_cities
        query = self.var_city_search.get().strip()
        if len(query) < 2:
            self.city_search_frame.pack_forget()
            return
        results = search_cities(query)[:30]
        self.city_listbox.delete(0, "end")
        if results:
            for city in results:
                self.city_listbox.insert("end", city)
            self.city_search_frame.pack(fill="x", padx=15, pady=(0, 6))
        else:
            self.city_search_frame.pack_forget()

    def _on_city_double_click(self, event):
        selection = self.city_listbox.curselection()
        if selection:
            city = self.city_listbox.get(selection[0])
            self._add_cities([city])
            self.var_city_search.set("")
            self.city_search_frame.pack_forget()

    def _count_cities(self):
        try:
            cities = self._get_cities()
            self.lbl_city_count.configure(text=f"{len(cities)} cities queued")
        except:
            pass


    def _get_cities(self) -> list:
        text = self.var_custom_cities.get("1.0", "end-1c").strip()
        cities = [c.strip() for c in text.split("\n") if c.strip()]
        return cities

    def _get_scrape_config(self) -> dict:
        return {
            "business_type": self.var_business_type.get(),
            "cities": self._get_cities(),
            "max_per_city": int(self.var_max_per_city.get()),
            "min_reviews": int(self.var_min_reviews.get()),
            "max_reviews": int(self.var_max_reviews.get()),
            "min_delay": self.var_min_delay.get(),
            "max_delay": self.var_max_delay.get(),
            "headless": self.var_headless.get(),
            "skip_with_chatbot": self.var_skip_chatbot.get(),
            "require_email": self.var_require_email.get(),
        }

    def _start_scrape(self):
        cfg = self._get_scrape_config()

        if not cfg["cities"]:
            messagebox.showerror("No Cities", "Please add at least one city to target.")
            return
        if not cfg["business_type"]:
            messagebox.showerror("No Business Type", "Please select a business type.")
            return

        self._save_config()

        from core.scraper import ScraperEngine

        def on_progress(pct, lead):
            self.var_scrape_progress.set(pct / 100)
            self.lbl_scrape_status.configure(
                text=f"Scraping... {pct:.0f}% \u2014 Latest: {lead.name[:40]}")
            self._update_stats()

        def run():
            try:
                engine = ScraperEngine(
                    cfg,
                    progress_callback=on_progress,
                    log_callback=self._log
                )
                self._scraper_engine = engine
                new_leads = engine.run_scrape()

                # Apply filters
                if cfg.get("skip_with_chatbot"):
                    new_leads = [l for l in new_leads if not l.has_chatbot]
                if cfg.get("require_email"):
                    new_leads = [l for l in new_leads if l.email]

                self.leads.extend(new_leads)
                self._log(f"\U0001f389 Done! {len(new_leads)} new leads added. Total: {len(self.leads)}", "success")
                self.lbl_scrape_status.configure(
                    text=f"\u2705 Complete \u2014 {len(new_leads)} leads found")
                self.var_scrape_progress.set(1.0)
                self._refresh_leads_table()
                self._update_stats()
            except Exception as e:
                self._log(f"\u274c Scrape failed: {e}", "error")
                self.lbl_scrape_status.configure(text=f"\u274c Error: {e}")
            finally:
                self._scraper_engine = None

        self.scraper_thread = threading.Thread(target=run, daemon=True)
        self.scraper_thread.start()
        self._log(f"\U0001f680 Starting scrape: {cfg['business_type']} in {len(cfg['cities'])} cities", "info")
        self.lbl_scrape_status.configure(text="Starting...")

    def _stop_scrape(self):
        if self._scraper_engine:
            self._scraper_engine.stop()
        self._log("\u23f9 Stop requested...", "warning")

    # ─── AI Provider Methods ─────────────────────────────────────────

    def _on_provider_change(self, provider: str):
        from core.outreach import AI_PROVIDERS
        info = AI_PROVIDERS.get(provider, {})
        models = info.get("models", [])

        if provider == "Ollama (Local)":
            # Try to fetch live models
            models = self._get_ollama_models_list()
            self.lbl_provider_hint.configure(
                text="\U0001f4a1 Ollama selected. Make sure 'ollama serve' is running. Pull models with: ollama pull llama3.2",
                text_color="#f59e0b"
            )
        else:
            self.lbl_provider_hint.configure(
                text=f"Using key from API Keys tab. Get key: {info.get('key_url', '')}",
                text_color="#475569"
            )

        if models:
            self.ai_model_menu.configure(values=models)
            recommended = info.get("recommended", models[0])
            self.var_ai_model.set(recommended)
        else:
            self.ai_model_menu.configure(values=["(no models found \u2014 is Ollama running?)"])
            self.var_ai_model.set("(no models found \u2014 is Ollama running?)")

    def _get_ollama_models_list(self) -> list:
        from core.outreach import get_ollama_models
        host = self.var_ollama_host.get().strip() or "localhost:11434"
        models = get_ollama_models(host)
        if models:
            self._log(f"\U0001f999 Ollama: found {len(models)} local models", "success")
            self.lbl_ollama_status.configure(text=f"\u25cf {len(models)} models", text_color="#10b981")
        else:
            self._log("\u26a0\ufe0f Ollama: no models found. Is 'ollama serve' running?", "warning")
            self.lbl_ollama_status.configure(text="\u25cf not running", text_color="#ef4444")
        return models

    def _refresh_ollama_models(self):
        models = self._get_ollama_models_list()
        if models:
            self.ai_model_menu.configure(values=models)
            self.var_ai_model.set(models[0])
            messagebox.showinfo("Ollama Models", f"Found {len(models)} models:\n\n" + "\n".join(models))
        else:
            messagebox.showerror("Ollama Not Found",
                "Could not connect to Ollama.\n\n"
                "Make sure Ollama is installed and running:\n"
                "  ollama serve\n\n"
                "Install: https://ollama.ai")

    def _check_ollama(self):
        from core.outreach import check_ollama_running, get_ollama_models
        host = self.var_ollama_host.get().strip() or "localhost:11434"
        running = check_ollama_running(host)
        if running:
            models = get_ollama_models(host)
            self.lbl_ollama_status.configure(
                text=f"\u25cf running \u00b7 {len(models)} models", text_color="#10b981")
            self._log(f"\U0001f999 Ollama running at {host} \u2014 {len(models)} models available", "success")
        else:
            self.lbl_ollama_status.configure(text="\u25cf not running", text_color="#ef4444")
            self._log(f"\u274c Ollama not reachable at {host}. Run: ollama serve", "error")

    def _test_ai_connection(self):
        self._log("\U0001f9ea Testing AI connection...", "info")

        def run():
            from core.outreach import AIPersonalizer
            p = AIPersonalizer(
                provider=self.var_ai_provider.get(),
                model=self.var_ai_model.get(),
                api_key=self._get_active_api_key(),
                ollama_host=self.var_ollama_host.get().strip(),
                your_name=self.var_your_name.get() or "Test User",
                your_website=self.var_your_website.get() or "example.com",
                your_email=self.var_your_email_sig.get() or "test@example.com",
                service_description=self.var_service_desc.get("1.0", "end-1c"),
                tone=self.var_ai_tone.get(),
            )
            ok, msg = p.test_connection()
            if ok:
                self._log(f"\u2705 AI test passed ({self.var_ai_provider.get()} / {self.var_ai_model.get()})", "success")
                messagebox.showinfo("AI Test", msg)
            else:
                self._log(f"\u274c AI test failed: {msg}", "error")
                messagebox.showerror("AI Test Failed", msg)

        threading.Thread(target=run, daemon=True).start()

    def _get_active_api_key(self) -> str:
        """Get the right API key based on selected provider"""
        provider = self.var_ai_provider.get()
        if provider == "Claude (Anthropic)":
            return self.var_anthropic_key.get().strip()
        elif provider == "ChatGPT (OpenAI)":
            return self.var_openai_key.get().strip()
        elif provider == "Gemini (Google)":
            return self.var_gemini_key.get().strip()
        return ""

    def _generate_emails(self):
        if not self.leads:
            messagebox.showwarning("No Leads", "Scrape leads first.")
            return

        min_score = int(self.var_min_score.get())
        targets = [l for l in self.leads if l.score >= min_score and l.status == "new"]

        if not targets:
            messagebox.showinfo("No Targets",
                f"No new leads with score >= {min_score}.")
            return

        provider = self.var_ai_provider.get()
        model = self.var_ai_model.get()
        api_key = self._get_active_api_key()

        if provider != "Ollama (Local)" and not api_key:
            messagebox.showerror("No API Key",
                f"Enter your {provider} API key in the API Keys tab.")
            return

        self._log(f"\U0001f916 Generating emails with {provider} / {model} for {len(targets)} leads...", "info")
        self.lbl_send_status.configure(text=f"Generating with {provider}...")

        from core.outreach import AIPersonalizer

        def run():
            personalizer = AIPersonalizer(
                provider=provider,
                model=model,
                api_key=api_key,
                ollama_host=self.var_ollama_host.get().strip(),
                your_name=self.var_your_name.get(),
                your_website=self.var_your_website.get(),
                your_email=self.var_your_email_sig.get(),
                service_description=self.var_service_desc.get("1.0", "end-1c"),
                email_template=self.var_email_template.get("1.0", "end-1c"),
                tone=self.var_ai_tone.get(),
            )

            for i, lead in enumerate(targets):
                try:
                    lead.ai_email_draft = personalizer.generate_email(lead)
                    self._log(f"  \u270d\ufe0f [{provider}] Email ready for {lead.name}", "success")
                except Exception as e:
                    self._log(f"  \u26a0\ufe0f Failed for {lead.name}: {e}", "warning")

                self.lbl_send_status.configure(
                    text=f"Generating... {i+1}/{len(targets)} [{provider}]")

            self._log(f"\u2705 Done! {len(targets)} emails generated by {provider} / {model}", "success")
            self.lbl_send_status.configure(
                text=f"\u2705 {len(targets)} emails ready ({provider} / {model})")
            self._refresh_leads_table()

        threading.Thread(target=run, daemon=True).start()


    def _start_send(self):
        gmail = self.var_gmail.get().strip()
        password = self.var_gmail_pass.get().strip()

        if not gmail or not password:
            messagebox.showerror("Missing Credentials",
                                 "Enter your Gmail credentials in the API Keys tab.")
            return

        sendable = [l for l in self.leads if l.email and l.ai_email_draft and l.status == "new"]
        if not sendable:
            messagebox.showinfo("Nothing to Send",
                                "Generate AI emails first, and make sure leads have emails found.")
            return

        if not messagebox.askyesno("Confirm Send",
                                   f"Send emails to {len(sendable)} leads?\n\n"
                                   f"Daily limit: {int(self.var_daily_limit.get())}"):
            return

        self._stop_send = False
        self._log(f"\U0001f4e4 Starting send to {len(sendable)} leads...", "info")

        from core.sender import EmailSender

        def on_progress(sent, total, lead, stats):
            pct = sent / total
            self.var_send_progress.set(pct)
            self.lbl_send_status.configure(
                text=f"Sending... {sent}/{total} \u2014 {lead.name[:30]}")

        def run():
            sender = EmailSender(
                gmail_address=gmail,
                gmail_app_password=password,
                daily_limit=int(self.var_daily_limit.get()),
                min_delay=self.var_email_min_delay.get(),
                max_delay=self.var_email_max_delay.get(),
                log_callback=self._log,
            )
            stats = sender.send_batch(
                sendable,
                progress_callback=on_progress,
                stop_flag_fn=lambda: self._stop_send
            )
            self.lbl_send_status.configure(
                text=f"\u2705 Done \u2014 {stats['sent']} sent, {stats['failed']} failed")
            self._update_stats()
            self._refresh_leads_table()

        threading.Thread(target=run, daemon=True).start()

    def _stop_send_fn(self):
        self._stop_send = True
        self._log("\u23f9 Send stopped.", "warning")

    def _test_gmail(self):
        gmail = self.var_gmail.get().strip()
        password = self.var_gmail_pass.get().strip()
        if not gmail or not password:
            messagebox.showerror("Missing", "Enter Gmail and App Password first.")
            return

        from core.sender import EmailSender
        sender = EmailSender(gmail, password)
        ok, msg = sender.test_connection()
        if ok:
            messagebox.showinfo("Connection Test", msg)
        else:
            messagebox.showerror("Connection Test", msg)
        self._log(msg, "success" if ok else "error")

    def _refresh_leads_table(self):
        status_filter = self.var_filter_status.get()
        score_filter = int(self.var_filter_score.get())

        filtered = [l for l in self.leads
                    if (status_filter == "all" or l.status == status_filter)
                    and l.score >= score_filter]

        # Sort by score descending
        filtered.sort(key=lambda l: l.score, reverse=True)

        self.leads_text.configure(state="normal")
        self.leads_text.delete("1.0", "end")

        # Header
        header = f"{'#':<4} {'BUSINESS NAME':<35} {'CITY':<25} {'EMAIL':<35} {'SCORE':<7} {'CHATBOT':<10} {'REVIEWS':<9} {'STATUS':<10} {'EMAIL READY'}\n"
        self.leads_text.insert("end", header, "header")
        self.leads_text.insert("end", "\u2500" * 160 + "\n", "sep")

        for i, lead in enumerate(filtered, 1):
            has_email_draft = "\u2705" if lead.ai_email_draft else "\u2500"
            has_bot = "\u26a0\ufe0f YES" if lead.has_chatbot else "no"
            row = (f"{i:<4} {lead.name[:34]:<35} {lead.address[:24]:<25} "
                   f"{lead.email[:34]:<35} {lead.score:<7} {has_bot:<10} "
                   f"{lead.review_count:<9} {lead.status:<10} {has_email_draft}\n")

            tag = "emailed" if lead.status == "emailed" else (
                "high" if lead.score >= 70 else
                "mid" if lead.score >= 45 else "low"
            )
            self.leads_text.insert("end", row, tag)

        self.leads_text.insert("end", f"\n\u2500\u2500\u2500 {len(filtered)} leads shown \u2500\u2500\u2500\n", "sep")
        self.leads_text.configure(state="disabled")

    def _export_leads(self, fmt: str = None):
        if not self.leads:
            messagebox.showwarning("No Leads", "Nothing to export yet.")
            return

        from core.exporter import ExportManager
        em = ExportManager()

        if fmt == "csv":
            path = em.export_csv(self.leads)
            fmt_name = "CSV"
        elif fmt == "xlsx":
            path = em.export_excel(self.leads)
            fmt_name = "Excel"
        elif fmt == "json":
            path = em.export_json(self.leads)
            fmt_name = "JSON"
        else:
            # Default: ask user
            if messagebox.askyesno("Export", "Export as CSV? (No = Excel)"):
                path = em.export_csv(self.leads)
                fmt_name = "CSV"
            else:
                path = em.export_excel(self.leads)
                fmt_name = "Excel"

        self._log(f"\U0001f4be Exported {len(self.leads)} leads as {fmt_name} to {path}", "success")
        messagebox.showinfo("Exported", f"Saved {len(self.leads)} leads to:\n{path}")

    def _load_leads(self):
        path = filedialog.askopenfilename(
            title="Load Leads JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            from core.exporter import ExportManager
            loaded = ExportManager().load_json(path)
            self.leads.extend(loaded)
            self._log(f"\U0001f4c2 Loaded {len(loaded)} leads from {path}", "success")
            self._refresh_leads_table()
            self._update_stats()
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _update_stats(self):
        total = len(self.leads)
        emailed = sum(1 for l in self.leads if l.status == "emailed")
        self.lbl_stats.configure(text=f"{total} leads found\n{emailed} emails sent")
