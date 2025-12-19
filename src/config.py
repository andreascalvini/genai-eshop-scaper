"""Configuration management for the eShop scraper application."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    llm_mode: str = "perplexity"  # "perplexity" or "local"
    perplexity_api_key: str = ""
    ollama_model_name: str = "llama2"  # Local model name for Ollama
    ollama_base_url: str = "http://localhost:11434"  # Ollama default URL
    langchain_api_key: Optional[str] = None

    # Crawling Configuration
    max_depth: int = 3
    max_pages: int = 100
    request_timeout: int = 10
    retry_attempts: int = 3

    # LangGraph Configuration
    langgraph_trace_enabled: bool = False

    # User Agent for requests
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()
