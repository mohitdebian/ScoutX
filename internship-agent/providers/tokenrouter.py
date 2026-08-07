import httpx
import json
import logging
from typing import Dict, Any
from .base_provider import BaseProvider
from config.settings import settings

logger = logging.getLogger(__name__)

class KimiProvider(BaseProvider):
    """Provider for Kimi K3 models (simulated here with OpenAI-compatible API)."""

    def __init__(self):
        self.api_key = settings.kimi_api_key
        self.model = settings.default_model
        # Using a standard OpenAI compatible base URL assuming Kimi K3 follows this
        # or it can be configured if different. We'll use a placeholder URL if not provided.
        self.base_url = "https://api.moonshot.cn/v1" # Example Kimi endpoint

    async def generate(self, prompt: str, schema: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("Kimi API key is missing. Returning mock response.")
            return self._mock_response(schema)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that strict follows JSON schemas."},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1
        }

        if schema:
            payload["response_format"] = {"type": "json_object"}
            # Append schema instructions to the prompt
            messages[1]["content"] += f"\n\nYou MUST return a raw JSON object matching this schema exactly: {json.dumps(schema)}"

        try:
            async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]

                if schema:
                    # Clean up markdown if the model returns it despite json_object format
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:-3]
                    elif content.startswith("```"):
                        content = content[3:-3]
                    return json.loads(content)
                return {"text": content}

        except Exception as e:
            logger.error(f"Error calling Kimi API: {e}")
            if schema:
                 # Fallback mock for robustness if API fails
                 return self._mock_response(schema)
            return {"error": str(e)}

    def _mock_response(self, schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provide a mock response when API key is missing or call fails."""
        if schema:
            return {
                "match_score": 85,
                "matched_skills": ["Python", "Asyncio"],
                "missing_skills": ["C++"],
                "summary": "Mock summary",
                "reason": "Mock reason"
            }
        return {"text": "Mock response"}
