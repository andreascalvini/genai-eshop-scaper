# Project Structure Overview

```
genai-eshop-scraper/
│
├── src/                          # Main application code
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── workflow.py              # LangGraph workflow definition
│   ├── main.py                  # Application entry point
│   │
│   ├── agents/                  # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py              # Base agent class (abstract)
│   │   ├── page_fetching.py     # HTTP fetching agent (code-based)
│   │   ├── page_discovery.py    # URL discovery agent (code-based)
│   │   └── product_extraction.py # Product extraction agent (LLM-based)
│   │
│   ├── models/                  # Pydantic data models
│   │   ├── __init__.py
│   │   ├── product.py           # Product and ProductVariant models
│   │   └── crawl_state.py       # CrawlState model for workflow
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── http.py              # HTTP request utilities
│       ├── parser.py            # HTML parsing utilities
│       └── requirements.txt      # Utils-specific dependencies
│
├── tests/                        # Test suite
│   └── test_models.py           # Model tests
│
├── Configuration Files
│   ├── pyproject.toml           # Project metadata and dependencies
│   ├── .env.example             # Environment variables template
│   └── .gitignore               # Git ignore rules
│
├── Documentation
│   ├── README.md                # Main documentation
│   ├── QUICKSTART.md            # 5-minute quick start guide
│   ├── ARCHITECTURE.md          # Detailed architecture documentation
│   └── PROJECT_STRUCTURE.md     # This file
│
├── Examples & Build
│   ├── example_usage.py         # Example usage script
│   ├── Makefile                 # Common commands
│   └── products.json            # Output file (generated)
│       crawl_report.json        # Report file (generated)
```

## File Descriptions

### Core Application (`src/`)

#### `config.py`
- Loads environment variables using Pydantic
- Manages all application settings
- Settings: OpenAI API key, crawl limits, timeouts, etc.

#### `workflow.py`
- Defines the LangGraph workflow
- Creates nodes for each agent
- Defines transitions and conditional logic
- Compiles the graph for execution

#### `main.py`
- Application entry point
- Handles command-line interface
- Orchestrates the crawl execution
- Saves results to JSON files

### Agents (`src/agents/`)

#### `base.py`
- Abstract base class for all agents
- Defines the `run()` interface
- Common agent initialization

#### `page_fetching.py` (Code-based)
- Fetches HTML from URLs
- Implements retry logic with exponential backoff
- Tracks failed requests
- Configurable timeouts and user-agents

#### `page_discovery.py` (Code-based)
- Extracts links from HTML
- Filters links (same domain, not visited)
- Enforces depth and page count limits
- Manages URL queue

#### `product_extraction.py` (LLM-based)
- Uses OpenAI LLM to extract product data
- Parses structured JSON output
- Fallback to basic extraction if LLM unavailable
- Validates extracted products

### Data Models (`src/models/`)

#### `product.py`
- `Product`: Complete product information
- `ProductVariant`: Size/color/price variants

#### `crawl_state.py`
- `CrawlState`: State object for LangGraph
- Passed between all agents
- Maintains crawl progress and results

### Utilities (`src/utils/`)

#### `http.py`
- `fetch_url()`: Async URL fetching
- `fetch_url_sync()`: Synchronous wrapper
- Includes retry logic and error handling

#### `parser.py`
- `extract_links()`: Extract URLs from HTML
- `is_same_domain()`: Domain matching
- `get_domain()`: Extract domain from URL
- `extract_text()`: Clean text extraction

## Workflow Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│ User provides start URL                                 │
│ (e.g., https://example.com/shop)                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Initialize CrawlState                                   │
│ - Set start_url                                         │
│ - Initialize urls_to_visit = [start_url]                │
│ - Initialize empty products list                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ LangGraph Execution Loop                                │
└─────────────────┬───────────────────────────────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
┌──────────────┐      ┌────────────────┐
│ Page Fetch   │      │ Should Loop?   │
│ Agent        │      │                │
├──────────────┤      ├────────────────┤
│ Input: URL   │◄─────│ More URLs? AND │
│ Output: HTML │      │ <Max Pages?    │
└──────────────┘      └────────────────┘
      │                       ▲
      │                       │ YES
      │                       │
      ▼                       │
┌──────────────┐              │
│ Page Disc.   │              │
│ Agent        │              │
├──────────────┤              │
│ Input: HTML  │              │
│ Output: URLs ├──────────────┘
└──────────────┘
      │
      │ NO (all done)
      │
      ▼
┌──────────────┐
│ Product      │
│ Extract      │
│ Agent        │
├──────────────┤
│ Input: HTML  │
│ Output: Prod.│
└──────────────┘
      │
      ▼
┌──────────────┐
│ Save Results │
│ - products.  │
│   json       │
│ - crawl_     │
│   report.json│
└──────────────┘
```

## Data Flow Diagram

```
Input URL
    │
    ▼
CrawlState (start_url, urls_to_visit=[url])
    │
    ├─► PageFetchingAgent
    │   └─► HTML Content
    │       └─► CrawlState (page_html, visited_urls++)
    │
    ├─► PageDiscoveryAgent
    │   └─► New URLs
    │       └─► CrawlState (urls_to_visit++, discovered_urls++)
    │
    └─► ProductExtractionAgent
        └─► Product Objects
            └─► CrawlState (products++, total_products_found++)
                │
                └─► JSON Output Files
                    ├─ products.json
                    └─ crawl_report.json
```

## Agent Interaction

```
PageFetchingAgent
  │
  ├─ Depends on: URLs in state.urls_to_visit
  ├─ Updates: state.page_html, state.visited_urls
  └─ Provides HTML to ► PageDiscoveryAgent & ProductExtractionAgent
                          │              │
                          │              └─ Extracts products using LLM
                          │
                          └─ Extracts new URLs to crawl

PageDiscoveryAgent
  │
  ├─ Depends on: state.page_html (from PageFetchingAgent)
  ├─ Updates: state.urls_to_visit, state.discovered_urls
  └─ Respects: MAX_DEPTH, MAX_PAGES settings

ProductExtractionAgent
  │
  ├─ Depends on: state.page_html (from PageFetchingAgent)
  ├─ Uses: OpenAI API (optional)
  ├─ Updates: state.products, state.total_products_found
  └─ Fallback: Code-based extraction if LLM unavailable
```

## Dependency Graph

```
main.py
  ├─ workflow.py
  │   └─ agents/* (all three agents)
  │
  ├─ agents/page_fetching.py
  │   └─ utils/http.py
  │
  ├─ agents/page_discovery.py
  │   ├─ utils/parser.py
  │   └─ config.py
  │
  ├─ agents/product_extraction.py
  │   ├─ utils/parser.py
  │   ├─ models/product.py
  │   └─ langchain (optional)
  │
  ├─ models/crawl_state.py
  │   └─ models/product.py
  │
  └─ config.py
      └─ pydantic_settings
```

## Configuration Hierarchy

```
Environment Variables (.env)
           │
           ▼
    Settings (config.py)
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
Agents  Workflow  Models
```

## Output Files

### products.json
```
Root
├─ timestamp: ISO datetime
├─ total_products: integer
└─ products: array of Product objects
    └─ Each product includes:
        ├─ product_code
        ├─ name
        ├─ brand
        ├─ category
        ├─ base_price
        ├─ variants (array)
        ├─ url
        ├─ source_domain
        └─ metadata
```

### crawl_report.json
```
Root
├─ timestamp: ISO datetime
├─ summary
│   ├─ start_url
│   ├─ total_pages_crawled
│   ├─ total_urls_discovered
│   ├─ total_products_found
│   └─ failed_urls count
└─ failed_urls
    └─ url: error message
```

## Key Design Patterns

1. **Agent Pattern**: Each agent has a single responsibility
2. **State Pattern**: CrawlState flows through the workflow
3. **Pipeline Pattern**: Agents process data sequentially
4. **Factory Pattern**: Settings factory creates configuration
5. **Strategy Pattern**: LLM vs fallback extraction
