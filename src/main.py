"""Main application entry point."""

from src.models.crawl_state import CrawlState
from src.workflow import compile_graph
from src.config import settings
import json
from pathlib import Path
from datetime import datetime


def run_crawler(start_url: str, output_file: str = "products.json") -> CrawlState:
    """
    Run the eShop scraper workflow.

    Args:
        start_url: The main page URL to start crawling from
        output_file: Path to save extracted products

    Returns:
        Final crawl state with all results
    """
    print(f"\n{'='*60}")
    print(f"GenAI eShop Scraper - Starting Crawl")
    print(f"{'='*60}")
    print(f"Start URL: {start_url}")
    print(f"Max Depth: {settings.max_depth}")
    print(f"Max Pages: {settings.max_pages}")
    print(f"{'='*60}\n")

    # Initialize state
    initial_state = CrawlState(
        start_url=start_url,
        urls_to_visit=[start_url],
    )

    # Compile and run graph
    graph = compile_graph()

    print("Running workflow...\n")
    final_state = graph.invoke(initial_state)

    # Print results
    print(f"\n{'='*60}")
    print(f"Crawl Results")
    print(f"{'='*60}")
    print(f"Pages Crawled: {final_state.total_pages_crawled}")
    print(f"Products Found: {final_state.total_products_found}")
    print(f"Failed URLs: {len(final_state.failed_products)}")
    print(f"Status: {final_state.status}")
    print(f"{'='*60}\n")

    # Save results
    if final_state.products:
        save_products(final_state.products, output_file)
        print(f"✓ Products saved to {output_file}")

    # Save detailed report
    save_report(final_state)

    return final_state


def save_products(products: list, filename: str) -> None:
    """Save products to JSON file."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_products": len(products),
        "products": [json.loads(p.model_dump_json()) for p in products],
    }

    Path(filename).write_text(json.dumps(output, indent=2, default=str))


def save_report(state: CrawlState) -> None:
    """Save detailed crawl report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "start_url": state.start_url,
            "total_pages_crawled": state.total_pages_crawled,
            "total_urls_discovered": len(state.discovered_urls),
            "total_products_found": state.total_products_found,
            "failed_urls": len(state.failed_products),
        },
        "failed_urls": state.failed_products,
    }

    Path("crawl_report.json").write_text(json.dumps(report, indent=2))


def main() -> None:
    """Main entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.main <start_url> [output_file]")
        print("Example: python -m src.main https://example.com/shop products.json")
        sys.exit(1)

    start_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "products.json"

    try:
        run_crawler(start_url, output_file)
    except KeyboardInterrupt:
        print("\n\nCrawling interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
