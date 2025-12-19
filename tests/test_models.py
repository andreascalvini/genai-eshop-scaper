"""Example usage and testing."""

import pytest
from src.models import CrawlState, Product, ProductVariant
from decimal import Decimal


def test_crawl_state_initialization():
    """Test CrawlState initialization."""
    state = CrawlState(start_url="https://example.com")

    assert state.start_url == "https://example.com"
    assert state.urls_to_visit == []
    assert state.visited_urls == set()
    assert state.total_products_found == 0


def test_product_creation():
    """Test Product model creation."""
    variant = ProductVariant(size="M", price=Decimal("29.99"))

    product = Product(
        product_code="TEST-001",
        name="Test Product",
        base_price=Decimal("29.99"),
        url="https://example.com/product",
        source_domain="example.com",
        variants=[variant],
    )

    assert product.product_code == "TEST-001"
    assert len(product.variants) == 1
    assert product.variants[0].size == "M"


@pytest.mark.asyncio
async def test_url_extraction():
    """Test URL extraction from HTML."""
    from src.utils import extract_links

    html = """
    <html>
    <body>
        <a href="/page1">Link 1</a>
        <a href="/page2">Link 2</a>
        <a href="https://other.com">External</a>
    </body>
    </html>
    """

    links = extract_links(html, "https://example.com")

    assert "https://example.com/page1" in links
    assert "https://example.com/page2" in links
    assert "https://other.com" in links
