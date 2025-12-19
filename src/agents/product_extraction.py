"""Product extraction agent - LLM-based agent for extracting product information."""

from src.agents.base import BaseAgent
from src.models.crawl_state import CrawlState
from src.models.product import Product, ProductVariant
from src.utils import get_domain, extract_text
from typing import Optional
from decimal import Decimal
import json

import os

try:
    # ChatOpenAI from langchain_openai works with Perplexity's OpenAI-compatible API
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    # Ollama support for running local models
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class ProductExtractionAgent(BaseAgent):
    """
    LLM-based agent that extracts product information from HTML.

    Uses an LLM to intelligently identify and extract:
    - Product codes/SKUs
    - Product names
    - Descriptions
    - Prices and variants
    - Availability
    """

    def __init__(self):
        """Initialize the product extraction agent."""
        super().__init__("product_extraction")
        self.llm = None

        from src.config import settings
        llm_mode = os.getenv("LLM_MODE", settings.llm_mode)

        if llm_mode == "local" and OLLAMA_AVAILABLE:
            try:
                ollama_model = os.getenv("OLLAMA_MODEL_NAME", settings.ollama_model_name)
                ollama_url = os.getenv("OLLAMA_BASE_URL", settings.ollama_base_url)
                
                self.llm = Ollama(
                    model=ollama_model,
                    base_url=ollama_url,
                    temperature=0
                )
                print(f"[{self.name}] Using local Ollama model: {ollama_model}")
            except Exception as e:
                print(f"Failed to initialize local LLM: {e}")
        elif LANGCHAIN_AVAILABLE:
            try:
                api_key = os.getenv("PERPLEXITY_API_KEY")
                if not api_key:
                    api_key = settings.perplexity_api_key
                
                self.llm = ChatOpenAI(
                    model="llama-2-70b-chat",
                    temperature=0,
                    api_key=api_key,
                    base_url="https://api.perplexity.ai"
                )
                print(f"[{self.name}] Using Perplexity AI")
            except Exception as e:
                print(f"Failed to initialize LLM: {e}")

    def run(self, state: CrawlState) -> CrawlState:
        """
        Extract products from the current page HTML.

        Args:
            state: Current crawl state

        Returns:
            Updated crawl state with extracted products
        """
        if not state.page_html:
            state.error_message = "No HTML content to process"
            return state

        try:
            if self.llm:
                products = self._extract_with_llm(state)
            else:
                products = self._extract_fallback(state)

            state.products.extend(products)
            state.total_products_found += len(products)

            print(
                f"[{self.name}] Extracted {len(products)} products "
                f"from {state.current_url}"
            )

        except Exception as e:
            state.error_message = f"Product extraction failed: {str(e)}"
            state.failed_products[state.current_url] = str(e)

        return state

    def _extract_with_llm(self, state: CrawlState) -> list[Product]:
        """Extract products using LLM."""
        # Prepare text content for LLM
        text_content = extract_text(state.page_html)[:2000]  # Limit token count

        prompt = PromptTemplate(
            template="""Analyze this fashion ecommerce page and extract all products.
            
Page content:
{page_content}

Extract products with this JSON structure:
{{
  "products": [
    {{
      "product_code": "unique identifier/SKU",
      "name": "product name",
      "description": "short description",
      "brand": "brand name if available",
      "category": "product category",
      "base_price": "price as string",
      "variants": [
        {{"size": "S/M/L/etc", "color": "color", "sku": "variant sku", "price": "price"}}
      ]
    }}
  ]
}}

Return only valid JSON. If no products found, return {{"products": []}}.
""",
            input_variables=["page_content"],
        )

        try:
            # For Ollama, invoke directly; for ChatOpenAI, use with parser
            if isinstance(self.llm, ChatOpenAI):
                parser = JsonOutputParser()
                chain = prompt | self.llm | parser
                result = chain.invoke({"page_content": text_content})
            else:
                # Ollama returns raw text
                chain = prompt | self.llm
                response = chain.invoke({"page_content": text_content})
                # Try to parse JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"products": []}
            
            products = []
            for prod_data in result.get("products", []):
                try:
                    product = self._parse_product_data(
                        prod_data, state.current_url, get_domain(state.start_url)
                    )
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"Error parsing product: {e}")

            return products
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return []

    def _extract_fallback(self, state: CrawlState) -> list[Product]:
        """
        Fallback extraction when LLM is not available.

        Uses simple heuristics to find product patterns.
        """
        # This is a simple fallback - in production you'd use libraries
        # like BeautifulSoup with more sophisticated selectors
        products = []
        print(f"[{self.name}] Using fallback extraction (LLM not available)")
        return products

    def _parse_product_data(
        self, prod_data: dict, url: str, domain: str
    ) -> Optional[Product]:
        """Parse product data into Product model."""
        try:
            variants = []
            for var_data in prod_data.get("variants", []):
                variant = ProductVariant(
                    size=var_data.get("size", ""),
                    color=var_data.get("color"),
                    sku=var_data.get("sku"),
                    price=Decimal(str(var_data.get("price", 0))),
                )
                variants.append(variant)

            product = Product(
                product_code=prod_data.get("product_code", "UNKNOWN"),
                name=prod_data.get("name", ""),
                description=prod_data.get("description"),
                brand=prod_data.get("brand"),
                category=prod_data.get("category"),
                variants=variants,
                base_price=Decimal(str(prod_data.get("base_price", 0))),
                url=url,
                source_domain=domain,
            )
            return product
        except Exception as e:
            print(f"Error parsing product data: {e}")
            return None
