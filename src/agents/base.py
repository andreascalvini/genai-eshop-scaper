"""Agent base class and utilities."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from src.models.crawl_state import CrawlState


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str):
        """Initialize the agent.

        Args:
            name: Agent name
        """
        self.name = name

    @abstractmethod
    def run(self, state: CrawlState) -> CrawlState:
        """Execute the agent logic.

        Args:
            state: Current crawl state

        Returns:
            Updated crawl state
        """
        pass
