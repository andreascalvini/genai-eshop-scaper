"""Page relevance agent - heuristic-based detector for product pages."""

from src.agents.base import BaseAgent
from src.models.crawl_state import CrawlState
from src.utils.parser import extract_text
from bs4 import BeautifulSoup
import re


class PageRelevanceAgent(BaseAgent):
    """Agent that decides whether a fetched page likely contains products.

    Uses simple heuristics:
    - Presence of schema.org Product/Offer JSON-LD
    - Presence of currency/price patterns (€, $, £) or keywords
    - Presence of 'add to cart' / 'buy now' buttons
    """

    def __init__(self):
        super().__init__("page_relevance")

    def run(self, state: CrawlState) -> CrawlState:
        if not state.page_html:
            state.is_relevant = False
            return state

        html = state.page_html
        text = extract_text(html).lower()

        # 1) JSON-LD product detection
        try:
            soup = BeautifulSoup(html, "html.parser")
            scripts = soup.find_all("script", type="application/ld+json")
            for s in scripts:
                try:
                    data = s.string or ""
                    if data and ("\"@type\": \"Product\"" in data or '"@type": "Product"' in data or '"@type": "Offer"' in data):
                        state.is_relevant = True
                        return state
                except Exception:
                    continue
        except Exception:
            pass

        # 2) Price/currency heuristic
        if re.search(r"[\$€£]\s?\d", html) or re.search(r"\d+\s?(?:eur|€|usd|\$|£)", text):
            state.is_relevant = True
            return state

        # 3) Product-related keywords and CTAs
        keywords = [
            "add to cart",
            "add to bag",
            "buy now",
            "price",
            "sku",
            "size",
            "in stock",
            "out of stock",
            "add to wishlist",
            "product",
            "colour",
            "color",
            "add to basket",
        ]

        for kw in keywords:
            if kw in text:
                state.is_relevant = True
                return state

        # 4) Minimal image + price density heuristic
        try:
            imgs = soup.find_all("img")
            if len(imgs) >= 3 and re.search(r"price|€|£|\$", text):
                state.is_relevant = True
                return state
        except Exception:
            pass

        # If none matched, mark as not relevant
        state.is_relevant = False
        state.status = "skipped_not_relevant"
        print(f"[{self.name}] Skipping {state.current_url} (no product signals)")
        return state
