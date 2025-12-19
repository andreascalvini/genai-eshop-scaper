"""Data models for the eShop scraper."""

from .product import Product, ProductVariant
from .crawl_state import CrawlState

__all__ = ["Product", "ProductVariant", "CrawlState"]
