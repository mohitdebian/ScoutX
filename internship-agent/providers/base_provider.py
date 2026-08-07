from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a response given a prompt.
        If schema is provided, return a structured JSON response matching the schema.
        """
        pass
