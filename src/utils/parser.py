"""HTML parsing and URL extraction utilities."""

from bs4 import BeautifulSoup
from typing import Set, List
from urllib.parse import urljoin, urlparse


def extract_links(html: str, base_url: str) -> Set[str]:
    """
    Extract all links from HTML content.

    Args:
        html: HTML content to parse
        base_url: Base URL for resolving relative links

    Returns:
        Set of absolute URLs found in the HTML
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        links = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            # Remove fragments
            absolute_url = absolute_url.split("#")[0]
            links.add(absolute_url)

        return links
    except Exception as e:
        print(f"Error extracting links from {base_url}: {e}")
        return set()


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain.

    Args:
        url1: First URL
        url2: Second URL

    Returns:
        True if both URLs are from the same domain
    """
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    return domain1 == domain2


def get_domain(url: str) -> str:
    """
    Extract domain from URL.

    Args:
        url: URL to parse

    Returns:
        Domain name
    """
    return urlparse(url).netloc


def extract_text(html: str) -> str:
    """
    Extract all text content from HTML.

    Args:
        html: HTML content

    Returns:
        Plain text content
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator=" ", strip=True)
    except Exception:
        return ""
