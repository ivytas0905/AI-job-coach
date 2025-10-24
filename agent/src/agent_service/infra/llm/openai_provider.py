"""OpenAI LLM Provider Implementation"""
from typing import Optional
from openai import AsyncOpenAI
from ...domain.ports import LlmProviderPort
from ...config import get_settings

settings = get_settings()


class OpenAIProvider(LlmProviderPort):
    """OpenAI GPT implementation"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model name (defaults to settings)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or "gpt-4o-mini"
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text using OpenAI API

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

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
