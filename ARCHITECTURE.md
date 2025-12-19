# Architecture Documentation

## System Overview

The GenAI eShop Scraper is built on a modular, agent-based architecture using LangGraph for workflow orchestration. The system implements a multi-agent pattern where specialized agents handle different aspects of web scraping.

## Core Components

### 1. State Management (`CrawlState`)

The `CrawlState` object is the central data structure that flows through all agents in the LangGraph workflow.

**Key Fields:**
- `start_url`: Initial URL provided by the user
- `urls_to_visit`: Queue of URLs to be crawled
- `visited_urls`: Set of already crawled URLs
- `discovered_urls`: Set of all discovered URLs
- `products`: List of extracted `Product` objects
- `page_html`: Current page HTML content
- `depth`: Current crawl depth
- `status`: Workflow status (initialized, running, completed)

### 2. Agent Architecture

The system uses four specialized agents:

#### Page Fetching Agent (Code-based)
```
Responsibility: HTTP request handling
Input: URL from queue
Output: HTML content
Features:
- Retry logic with exponential backoff
- User-agent handling
- Timeout management
- Error tracking
```

**Implementation**: `src/agents/page_fetching.py`

#### Page Discovery Agent (Code-based)
```
Responsibility: URL discovery and filtering
Input: HTML content
Output: Filtered list of new URLs
Features:
- Link extraction from HTML
- Same-domain filtering
- Depth limiting
- URL deduplication
- Respects configuration limits (max_pages, max_depth)
```

**Implementation**: `src/agents/page_discovery.py`

#### Product Extraction Agent (LLM-based)
```
Responsibility: Intelligent product data extraction
Input: HTML content
Output: Structured product data
Features:
- LLM-powered extraction (GPT-3.5/GPT-4)
- JSON parsing and validation
- Fallback extraction method
- Error handling
- Handles: product codes, names, prices, sizes, variants, brands
```

**Implementation**: `src/agents/product_extraction.py`

#### Page Relevance Agent (Code-based)
```
Responsibility: Heuristic-based relevance detection
Input: HTML content
Output: `is_relevant` flag on `CrawlState`
Features:
- Detects `schema.org` `Product`/`Offer` JSON-LD
- Finds currency/price patterns and product CTAs ("add to cart", "buy now")
- Basic image + price density checks
- Marks page as not relevant to skip discovery and extraction
```

**Implementation**: `src/agents/page_relevance.py`

### 3. Data Models

#### Product Model
```python
Product(
    product_code: str,      # Unique identifier
    name: str,              # Product name
    description: str,       # Product description
    brand: str,            # Brand name
    category: str,         # Product category
    variants: List[ProductVariant],  # Size/color variants
    base_price: Decimal,   # Base price
    images: List[str],     # Product images
    url: str,              # Product page URL
    source_domain: str,    # Source website domain
    metadata: dict,        # Additional data
)
```

#### ProductVariant Model
```python
ProductVariant(
    size: str,             # Size (S, M, L, etc.)
    color: str,            # Color
    sku: str,              # Variant SKU
    price: Decimal,        # Variant price
    original_price: Decimal,  # Original price
    in_stock: bool,        # Stock status
    quantity_available: int,  # Available quantity
)
```

### 4. LangGraph Workflow

The workflow implements a sequential processing pattern with conditional looping:

```
┌─────────────────┐
│   START         │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  FETCH PAGE         │  (Page Fetching Agent)
│  - Get URL from    │
│    queue            │
│  - Fetch HTML      │
│  - Handle errors   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  RELEVANCE CHECK    │  (Page Relevance Agent)
│  - Detect Product   │
│    signals (JSON-LD,
│    price, CTAs)     │
│  - Set `is_relevant` flag
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  DISCOVER PAGES     │  (Page Discovery Agent)
│  - Extract links   │
│  - Filter by domain│
│  - Add to queue    │
│  - Check limits    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  EXTRACT PRODUCTS   │  (Product Extraction Agent)
│  - Use LLM to      │
│    extract data    │
│  - Parse output    │
│  - Store products  │
└────────┬────────────┘
         │
         ▼
    Should Continue?
    (Queue not empty AND
     Page limit not reached)
         │
    ┌────┴────┐
    │         │
   YES        NO
    │         │
    ▼         ▼
  FETCH     END
    │        └─► OUTPUT RESULTS
    │            - products.json
    │            - crawl_report.json
    └────────────┘
```

### 5. Configuration Management

The `Settings` class (Pydantic) manages environment variables:

```python
# LLM Configuration
OPENAI_API_KEY          # OpenAI API key
LANGCHAIN_API_KEY       # LangChain API key

# Crawling Configuration
MAX_DEPTH=3             # Max crawl depth from start URL
MAX_PAGES=100           # Max pages to crawl
REQUEST_TIMEOUT=10      # HTTP request timeout
RETRY_ATTEMPTS=3        # Retry attempts for failed requests

# LangGraph Configuration
LANGGRAPH_TRACE_ENABLED=false  # Enable LangGraph tracing
```

### 6. Utility Functions

#### HTTP Module (`src/utils/http.py`)
- `fetch_url()`: Async URL fetching with retries
- `fetch_url_sync()`: Synchronous wrapper

#### Parser Module (`src/utils/parser.py`)
- `extract_links()`: Extract links from HTML
- `is_same_domain()`: Domain matching
- `get_domain()`: Extract domain from URL
- `extract_text()`: Text extraction from HTML

## Data Flow

```
User Input (URL)
      │
      ▼
Initial CrawlState
      │
      ├─→ Fetch Page ──→ HTML Content
      │
      ├─→ Discover Pages ──→ New URLs Added to Queue
      │
      ├─→ Extract Products ──→ Product Objects
      │
      └─→ Conditional Loop Decision
            │
            ├─→ More Pages? ──→ Fetch Next Page
            │
            └─→ Limits Reached? ──→ Generate Output
                  │
                  ├─→ products.json
                  └─→ crawl_report.json
```

## Error Handling Strategy

### HTTP Errors
- **Retry Logic**: Exponential backoff (2s, 4s, 8s, ...)
- **Fallback**: Skip URL and continue
- **Tracking**: Logged in `failed_products` dict

### Parsing Errors
- **HTML Parsing**: BeautifulSoup handles malformed HTML
- **Product Extraction**: Graceful fallback to simple extraction
- **LLM Errors**: Fallback to code-based extraction

### Rate Limiting
- Respects `REQUEST_TIMEOUT` setting
- Configurable retry attempts
- User-agent rotation (optional enhancement)

## Extension Points

### Custom Agents

Create new agents by extending `BaseAgent`:

```python
from src.agents.base import BaseAgent
from src.models import CrawlState

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_agent")
    
    def run(self, state: CrawlState) -> CrawlState:
        # Custom logic
        return state
```

### Custom LLM Models

Modify `ProductExtractionAgent` to use different models:

```python
self.llm = ChatOpenAI(model="gpt-4", temperature=0)
```

### Custom Extraction Logic

Implement site-specific extractors:

```python
class AmazonExtractor(BaseAgent):
    def run(self, state: CrawlState) -> CrawlState:
        # Amazon-specific extraction logic
        pass
```

## Performance Characteristics

### Scalability Considerations

1. **Sequential Processing**: Current design processes one page at a time
2. **Memory Usage**: Stores all products in memory
3. **API Rate Limits**: Bounded by LLM API rate limits
4. **Network I/O**: Synchronous HTTP requests

### Optimization Opportunities

1. **Async Concurrency**: Convert to fully async with multiple concurrent fetches
2. **Batch Processing**: Process multiple pages in parallel
3. **Database**: Add database for persistent storage
4. **Caching**: Redis/SQLite for URL deduplication
5. **Distributed**: Multi-worker architecture for large-scale crawling

## Security Considerations

- **robots.txt**: Should be checked before crawling
- **User-Agent**: Spoofed to avoid detection
- **Rate Limiting**: Respects timeouts and retry logic
- **Content Validation**: Input validation on all URLs
- **API Keys**: Stored in environment variables, not in code

## Testing Strategy

### Unit Tests
- Model creation and validation
- URL extraction and filtering
- Configuration loading

### Integration Tests
- End-to-end workflow with mock data
- Agent interaction testing
- LangGraph workflow validation

### Performance Tests
- Crawl speed benchmarking
- Memory profiling
- API usage tracking

## Future Architecture Enhancements

1. **Message Queue**: Add Redis/RabbitMQ for distributed processing
2. **Database**: Implement MongoDB/PostgreSQL for persistence
3. **Microservices**: Separate agents into individual services
4. **Caching Layer**: Redis for URL deduplication and rate limit tracking
5. **Monitoring**: Prometheus metrics and logging
6. **Web UI**: Dashboard for configuration and monitoring
7. **Kubernetes**: Deploy as containerized services
