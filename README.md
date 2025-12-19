# GenAI eShop Scraper

A multi-agent, LLM-powered web scraper for fashion ecommerce shops built with LangGraph.

## Overview

This application uses a sophisticated agent-based architecture to:

1. **Discover Pages** - Crawl and discover all pages within an ecommerce site
2. **Fetch Content** - Fetch HTML content from discovered pages
3. **Extract Products** - Use LLMs to intelligently extract product information including:
   - Product codes/SKUs
   - Names and descriptions
   - Brands and categories
   - Sizes, colors, and variants
   - Prices and availability
   - Product images and URLs

## Architecture

### Multi-Agent System

The application uses a combination of LLM-based and code-based agents:

- **Page Fetching Agent** (Code-based) - Handles HTTP requests and error management
- **Page Discovery Agent** (Code-based) - Discovers new URLs and manages crawl depth
- **Product Extraction Agent** (LLM-based) - Intelligently extracts product data using GPT-3.5/GPT-4

### LangGraph Workflow

```
[Fetch Page] → [Discover Pages] → [Extract Products] → [Continue Loop/End]
```

The workflow:
1. Fetches a page from the queue
2. Discovers new pages and adds them to the queue
3. Extracts products using the LLM agent
4. Loops until all pages are processed or limits reached

## Project Structure

```
genai-eshop-scraper/
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── base.py         # Base agent class
│   │   ├── page_fetching.py
│   │   ├── page_discovery.py
│   │   └── product_extraction.py
│   ├── models/              # Data models
│   │   ├── product.py
│   │   └── crawl_state.py
│   ├── utils/               # Utility functions
│   │   ├── http.py
│   │   └── parser.py
│   ├── config.py            # Configuration management
│   ├── workflow.py          # LangGraph workflow
│   └── main.py              # Entry point
├── tests/                   # Unit tests
├── pyproject.toml           # Project configuration
├── .env.example             # Environment template
└── README.md
```

## Installation

1. **Clone the repository:**
   ```bash
   cd genai-eshop-scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   export OPENAI_API_KEY=your_key_here
   ```

## Configuration

Edit `.env` or environment variables:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Crawling Configuration
MAX_DEPTH=3              # Maximum crawl depth from start URL
MAX_PAGES=100            # Maximum pages to crawl
REQUEST_TIMEOUT=10       # HTTP request timeout in seconds
RETRY_ATTEMPTS=3         # Number of retries for failed requests

# LangGraph Configuration
LANGGRAPH_TRACE_ENABLED=false
```

## Usage

### Command Line

```bash
# Basic usage
python -m src.main https://example.com/shop

# With custom output file
python -m src.main https://example.com/shop my_products.json
```

### Python API

```python
from src.main import run_crawler

state = run_crawler(
    start_url="https://example.com/shop",
    output_file="products.json"
)

print(f"Found {state.total_products_found} products")
```

## Output

The application generates:

1. **products.json** - Extracted products in structured JSON format:
   ```json
   {
     "timestamp": "2024-01-15T10:30:00",
     "total_products": 42,
     "products": [
       {
         "product_code": "SHIRT-001",
         "name": "Blue Cotton T-Shirt",
         "brand": "FashionBrand",
         "category": "Shirts",
         "base_price": "29.99",
         "variants": [
           {
             "size": "M",
             "color": "Blue",
             "sku": "SHIRT-001-M-BLU",
             "price": "29.99"
           }
         ],
         "url": "https://example.com/products/shirt-001",
         "source_domain": "example.com"
       }
     ]
   }
   ```

2. **crawl_report.json** - Crawl statistics and errors:
   ```json
   {
     "timestamp": "2024-01-15T10:30:00",
     "summary": {
       "total_pages_crawled": 15,
       "total_products_found": 42,
       "failed_urls": 2
     },
     "failed_urls": {
       "https://example.com/error": "Connection timeout"
     }
   }
   ```

## Agent Details

### Page Fetching Agent
- **Type**: Code-based
- **Responsibility**: Fetch HTML content from URLs
- **Features**:
  - Retry logic with exponential backoff
  - User-agent spoofing
  - Timeout handling
  - Error tracking

### Page Discovery Agent
- **Type**: Code-based
- **Responsibility**: Extract and filter URLs from HTML
- **Features**:
  - Link extraction and normalization
  - Same-domain filtering
  - Depth limiting
  - Deduplication

### Product Extraction Agent
- **Type**: LLM-based (requires OpenAI API)
- **Responsibility**: Extract product information from page HTML
- **Features**:
  - LLM-powered intelligent extraction
  - Fallback to code-based extraction if LLM unavailable
  - Structured output parsing
  - Error handling and validation

## Advanced Configuration

### Using Different LLMs

Modify `src/agents/product_extraction.py` to use different models:

```python
self.llm = ChatOpenAI(model="gpt-4", temperature=0)  # Use GPT-4
```

### Custom Agent Implementation

Extend the `BaseAgent` class:

```python
from src.agents.base import BaseAgent
from src.models.crawl_state import CrawlState

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom_agent")
    
    def run(self, state: CrawlState) -> CrawlState:
        # Your custom logic
        return state
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Troubleshooting

### LLM Agent Not Working
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has access to the required models
- Monitor token usage for rate limits

### Pages Not Being Discovered
- Check `MAX_DEPTH` setting
- Verify `MAX_PAGES` limit
- Review failed URLs in `crawl_report.json`

### Product Extraction Issues
- Review failed product URLs
- Check HTML structure of target site
- Consider adjusting LLM model or prompt

## Performance Optimization

1. **Parallel Processing**: Modify workflow to fetch multiple pages simultaneously
2. **Caching**: Add Redis/SQLite caching for visited URLs
3. **Async Agents**: Convert agents to async for better concurrency
4. **LLM Batching**: Batch multiple products for extraction in single LLM call

## Future Enhancements

- [ ] Database integration for persistent storage
- [ ] Proxy rotation for large-scale crawling
- [ ] JavaScript rendering support (Selenium/Playwright)
- [ ] Image downloading and processing
- [ ] Advanced deduplication algorithms
- [ ] Price history tracking
- [ ] Web UI for configuration and monitoring
- [ ] Distributed crawling across multiple machines

## License

MIT

## Support

For issues and questions, please create an issue in the repository.
