"""Utility module."""

from .http import fetch_url, fetch_url_sync
from .parser import extract_links, is_same_domain, get_domain, extract_text

__all__ = [
    "fetch_url",
    "fetch_url_sync",
    "extract_links",
    "is_same_domain",
    "get_domain",
    "extract_text",
]
