"""Page fetching agent - Code-based agent for fetching and preparing pages."""

from src.agents.base import BaseAgent
from src.models.crawl_state import CrawlState
from src.utils import fetch_url_sync
from urllib.parse import urlparse


class PageFetchingAgent(BaseAgent):
    """
    Code-based agent that fetches URL content.

    Handles HTTP requests, caching, and error management.
    """

    def __init__(self):
        """Initialize the page fetching agent."""
        super().__init__("page_fetching")

    def run(self, state: CrawlState) -> CrawlState:
        """
        Fetch HTML content from a URL.

        Args:
            state: Current crawl state

        Returns:
            Updated crawl state with page HTML
        """
        if not state.urls_to_visit:
            state.status = "completed"
            return state

        # Get next URL to visit
        url = state.urls_to_visit.pop(0)

        # Check if already visited
        if url in state.visited_urls:
            return state

        state.current_url = url

        try:
            # Fetch the page
            html = fetch_url_sync(url)

            if html is None:
                state.failed_products[url] = "Failed to fetch URL"
                print(f"[{self.name}] Failed to fetch {url}")
            else:
                state.page_html = html
                state.visited_urls.add(url)
                state.total_pages_crawled += 1
                print(
                    f"[{self.name}] Successfully fetched {url} "
                    f"({len(html)} bytes)"
                )

        except Exception as e:
            state.error_message = f"Fetch error: {str(e)}"
            state.failed_products[url] = str(e)
            print(f"[{self.name}] Error fetching {url}: {e}")

        return state
