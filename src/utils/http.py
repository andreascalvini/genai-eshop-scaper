"""HTTP utilities for web scraping."""

import httpx
from typing import Optional
from src.config import settings
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(settings.retry_attempts),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def fetch_url(url: str, timeout: int = settings.request_timeout) -> Optional[str]:
    """
    Fetch a URL and return its HTML content with retry logic.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        HTML content or None if fetch failed
    """
    try:
        headers = {"User-Agent": settings.user_agent}
        async with httpx.AsyncClient(
            timeout=timeout, follow_redirects=True, headers=headers
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPError as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def fetch_url_sync(url: str, timeout: int = settings.request_timeout) -> Optional[str]:
    """
    Synchronous wrapper for fetching URLs.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        HTML content or None if fetch failed
    """
    return asyncio.run(fetch_url(url, timeout))
