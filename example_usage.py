"""Example usage demonstrating the scraper."""

if __name__ == "__main__":
    from src.main import run_crawler

    # Example: Crawl a fashion ecommerce site
    # Replace with an actual ecommerce URL
    start_url = "https://example.com/shop"

    # Run the crawler
    state = run_crawler(
        start_url=start_url,
        output_file="products.json",
    )

    # Access results
    print(f"\nTotal products extracted: {state.total_products_found}")
    print(f"Total pages crawled: {state.total_pages_crawled}")

    if state.products:
        print("\nFirst product:")
        first_product = state.products[0]
        print(f"  Code: {first_product.product_code}")
        print(f"  Name: {first_product.name}")
        print(f"  Price: ${first_product.base_price}")
        print(f"  Variants: {len(first_product.variants)}")
