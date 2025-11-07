"""Together AI LLM Provider Implementation"""
from typing import Optional
import httpx
from ...domain.ports import LlmProviderPort
from ...config import get_settings

settings = get_settings()


class TogetherProvider(LlmProviderPort):
    """Together AI implementation"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Together AI provider

        Args:
            api_key: Together AI API key (defaults to settings)
            model: Model name (defaults to settings)
        """
        self.api_key = api_key or settings.together_api_key
        self.model = model or settings.together_model
        self.base_url = "https://api.together.xyz/v1"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text using Together AI API

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Randomness (0-2)
            max_tokens: Maximum response length

        Returns:
            Generated text
        """
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            raise RuntimeError(f"Together AI API error: {str(e)}")
