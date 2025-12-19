"""Page discovery agent - Code-based agent for discovering new pages."""

from src.agents.base import BaseAgent
from src.models.crawl_state import CrawlState
from src.utils import extract_links, is_same_domain, fetch_url_sync
from src.config import settings
from typing import Set


class PageDiscoveryAgent(BaseAgent):
    """
    Code-based agent that discovers new pages from HTML content.

    This agent extracts links from the current page and filters them
    to stay within the same domain and respect crawl depth limits.
    """

    def __init__(self):
        """Initialize the page discovery agent."""
        super().__init__("page_discovery")

    def run(self, state: CrawlState) -> CrawlState:
        """
        Discover new pages from the current HTML content.

        Args:
            state: Current crawl state

        Returns:
            Updated crawl state with newly discovered URLs
        """
        if not state.page_html:
            state.error_message = "No HTML content to process"
            return state

        # Extract links from current page
        found_links = extract_links(state.page_html, state.current_url)

        # Filter links to same domain and not yet visited
        new_urls: Set[str] = set()
        for link in found_links:
            # Check same domain
            if not is_same_domain(link, state.start_url):
                continue

            # Check not already visited or queued
            if link in state.visited_urls or link in state.discovered_urls:
                continue

            # Check depth limit
            if state.depth >= settings.max_depth:
                continue

            # Check total pages limit
            if len(state.discovered_urls) >= settings.max_pages:
                break

            new_urls.add(link)

        # Update state
        state.discovered_urls.update(new_urls)
        state.urls_to_visit.extend(list(new_urls))

        print(
            f"[{self.name}] Found {len(new_urls)} new URLs. "
            f"Total discovered: {len(state.discovered_urls)}"
        )

        return state
