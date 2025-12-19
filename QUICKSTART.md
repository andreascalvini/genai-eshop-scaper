# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
# Navigate to project directory
cd genai-eshop-scraper

# Install the package in development mode
pip install -e .
```

### 2. Configure OpenAI API

```bash
# Set your API key
export OPENAI_API_KEY="sk-..."

# Or create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Your First Scrape

```bash
# Run the crawler (replace with a real ecommerce site)
python -m src.main https://example.com/shop products.json
```

## Example Walkthrough

Let's say you want to scrape a fashion store. Here's what happens:

```python
# 1. You provide a start URL
start_url = "https://fashionstore.com/women"

# 2. The system initializes and starts the workflow
# 3. Each agent runs in sequence:
#    - Page Fetching Agent: Downloads https://fashionstore.com/women
#    - Page Discovery Agent: Finds links like /women/dresses, /women/shirts, etc.
#    - Product Extraction Agent: Uses LLM to extract product details
#    - Loop continues for each discovered page until limits reached

# 4. Results are saved
# products.json contains all extracted products
# crawl_report.json contains statistics and errors
```

## Configuration Tuning

### For Small Sites (< 50 products)
```bash
MAX_DEPTH=2           # Shallower crawl
MAX_PAGES=20          # Fewer pages
REQUEST_TIMEOUT=10    # Standard timeout
```

### For Large Sites (100+ products)
```bash
MAX_DEPTH=4           # Deeper crawl
MAX_PAGES=200         # More pages
REQUEST_TIMEOUT=30    # Longer timeout
RETRY_ATTEMPTS=5      # More retries for reliability
```

### Cost-Effective (reduce LLM usage)
```bash
# Use GPT-3.5-turbo instead of GPT-4
# Batch multiple products per LLM call
# Cache results for duplicate URLs
```

## Understanding the Output

### products.json
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "total_products": 42,
  "products": [
    {
      "product_code": "DRESS-001",
      "name": "Red Summer Dress",
      "brand": "FashionBrand",
      "category": "Women's Dresses",
      "base_price": "49.99",
      "variants": [
        {
          "size": "XS",
          "color": "Red",
          "sku": "DRESS-001-XS-RED",
          "price": "49.99"
        }
      ],
      "url": "https://fashionstore.com/products/red-summer-dress",
      "source_domain": "fashionstore.com"
    }
  ]
}
```

### crawl_report.json
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "summary": {
    "start_url": "https://fashionstore.com/women",
    "total_pages_crawled": 15,
    "total_urls_discovered": 42,
    "total_products_found": 42,
    "failed_urls": 0
  },
  "failed_urls": {}
}
```

## Common Tasks

### Process the Output

```python
import json

# Load products
with open("products.json") as f:
    data = json.load(f)

# Get all dresses
dresses = [p for p in data["products"] if "dress" in p["name"].lower()]

# Find products under $50
affordable = [p for p in data["products"] if float(p["base_price"]) < 50]

# Export to CSV
import csv
with open("products.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["product_code", "name", "base_price"])
    writer.writerows(data["products"])
```

### Debug Issues

```bash
# Check the crawl report for failed URLs
cat crawl_report.json | jq '.failed_urls'

# See which pages were crawled
cat crawl_report.json | jq '.summary'

# Verify products were extracted
cat products.json | jq '.products | length'
```

### Adjust for Specific Sites

Some ecommerce sites have unique HTML structures. You may need to:

1. **Disable LLM extraction** (if it's not working well):
   - Modify `ProductExtractionAgent` to use code-based extraction
   - Implement site-specific selectors using BeautifulSoup

2. **Implement a custom agent** for specific sites:
   ```python
   class AmazonProductExtractor(BaseAgent):
       def run(self, state: CrawlState) -> CrawlState:
           # Amazon-specific extraction
           pass
   ```

3. **Add to workflow**:
   ```python
   # In workflow.py
   amazon_extractor = AmazonProductExtractor()
   graph.add_node("amazon_extract", lambda s: amazon_extractor.run(s))
   ```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No products extracted | Check if LLM is working, review site HTML structure, enable debugging |
| Too many failed URLs | Increase REQUEST_TIMEOUT, RETRY_ATTEMPTS |
| Running out of API quota | Reduce MAX_PAGES, use cheaper model (GPT-3.5-turbo) |
| Memory issues with large sites | Implement database storage instead of in-memory |
| Blocked by site (403/429 errors) | Implement proxy rotation, add delays |

## Next Steps

1. **Review [ARCHITECTURE.md](ARCHITECTURE.md)** - Understand the system design
2. **Check [README.md](README.md)** - Full documentation
3. **Explore [example_usage.py](example_usage.py)** - Code examples
4. **Run tests** - `pytest tests/ -v`
5. **Customize** - Implement site-specific agents as needed

## Support

For detailed issues:
- Check logs in terminal output
- Review `crawl_report.json` for failed URLs
- Examine first few products in `products.json`
- Enable LangGraph tracing: `LANGGRAPH_TRACE_ENABLED=true`
