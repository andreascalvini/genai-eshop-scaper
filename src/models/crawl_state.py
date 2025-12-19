"""State management for the crawling workflow."""

from typing import Any, Dict, List, Set
from pydantic import BaseModel, Field
from .product import Product


class CrawlState(BaseModel):
    """State object passed between LangGraph nodes."""

    # Input
    start_url: str = Field(..., description="Initial URL to crawl")

    # Discovery
    urls_to_visit: List[str] = Field(default_factory=list)
    visited_urls: Set[str] = Field(default_factory=set)
    discovered_urls: Set[str] = Field(default_factory=set)

    # Products
    products: List[Product] = Field(default_factory=list)
    failed_products: Dict[str, str] = Field(default_factory=dict)

    # Metadata
    depth: int = 0
    current_url: str = ""
    page_html: str = ""
    error_message: str = ""
    status: str = "initialized"

    # Statistics
    total_pages_crawled: int = 0
    total_products_found: int = 0

    class Config:
        """Config for model."""

        arbitrary_types_allowed = True
