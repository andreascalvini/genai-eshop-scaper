"""LangGraph workflow orchestration for the eShop scraper."""

from langgraph.graph import StateGraph, END
from src.models.crawl_state import CrawlState
from src.agents import (
    PageFetchingAgent,
    PageDiscoveryAgent,
    ProductExtractionAgent,
)
from src.agents import PageRelevanceAgent
from src.config import settings
from typing import Literal


def create_crawl_graph() -> StateGraph:
    """
    Create the LangGraph workflow for crawling.

    The workflow follows this flow:
    1. Fetch a page from the queue
    2. Discover new pages on that page
    3. Extract products from that page
    4. Check if more pages to crawl -> loop back or end

    Returns:
        Compiled StateGraph
    """
    # Initialize agents
    page_fetcher = PageFetchingAgent()
    page_discoverer = PageDiscoveryAgent()
    product_extractor = ProductExtractionAgent()
    page_relevance = PageRelevanceAgent()

    # Create graph
    graph = StateGraph(CrawlState)

    # Define nodes
    def fetch_node(state: CrawlState) -> CrawlState:
        """Fetch a page from the queue."""
        return page_fetcher.run(state)

    def relevance_node(state: CrawlState) -> CrawlState:
        """Decide whether the current page is relevant (contains products)."""
        return page_relevance.run(state)

    def discover_node(state: CrawlState) -> CrawlState:
        """Discover new pages from the current page."""
        return page_discoverer.run(state)

    def extract_node(state: CrawlState) -> CrawlState:
        """Extract products from the current page."""
        return product_extractor.run(state)

    def should_continue(state: CrawlState) -> Literal["fetch", "end"]:
        """Determine if we should fetch more pages or end."""
        if state.urls_to_visit and len(state.visited_urls) < settings.max_pages:
            return "fetch"
        return "end"

    # Add nodes
    graph.add_node("fetch", fetch_node)
    graph.add_node("relevance", relevance_node)
    graph.add_node("discover", discover_node)
    graph.add_node("extract", extract_node)

    # Add edges
    graph.add_edge("fetch", "relevance")
    # If relevant -> discover, else skip discovery/extraction and fetch next
    graph.add_conditional_edges(
        "relevance",
        lambda s: "discover" if getattr(s, "is_relevant", True) else "fetch",
        {"discover": "discover", "fetch": "fetch"},
    )
    graph.add_edge("discover", "extract")
    graph.add_conditional_edges(
        "extract",
        should_continue,
        {
            "fetch": "fetch",
            "end": END,
        },
    )

    # Set entry point
    graph.set_entry_point("fetch")

    return graph


def compile_graph() -> StateGraph:
    """
    Compile the crawl graph.

    Returns:
        Compiled graph ready for execution
    """
    graph = create_crawl_graph()
    return graph.compile()
