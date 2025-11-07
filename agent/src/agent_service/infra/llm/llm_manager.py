"""LLM Manager with Fallback Support"""
from typing import Optional
import asyncio
import logging
from .openai_provider import OpenAIProvider
from .together_provider import TogetherProvider
from ...domain.ports import LlmProviderPort
from ...config import get_settings

logger = logging.getLogger(__name__)


class LLMManager:
    """
    LLM Manager with automatic fallback support.

    If the primary provider fails, automatically switches to fallback provider.
    Supports retry logic and automatic recovery.
    """

    def __init__(
        self,
        primary_provider: Optional[str] = None,
        fallback_provider: Optional[str] = None,
        enable_fallback: Optional[bool] = None
    ):
        """
        Initialize LLM Manager

        Args:
            primary_provider: Primary LLM provider ('openai' or 'together')
            fallback_provider: Fallback LLM provider
            enable_fallback: Whether to enable fallback (defaults to settings)
        """
        settings = get_settings()

        self.primary_provider_name = primary_provider or settings.llm_provider
        self.fallback_provider_name = fallback_provider or settings.fallback_provider
        self.enable_fallback = enable_fallback if enable_fallback is not None else settings.enable_fallback
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay

        # Initialize providers
        self.primary_provider = self._create_provider(self.primary_provider_name)
        self.fallback_provider = self._create_provider(self.fallback_provider_name) if self.enable_fallback else None

        # Track which provider is currently being used
        self.current_provider = self.primary_provider
        self.current_provider_name = self.primary_provider_name

        logger.info(f"LLM Manager initialized: primary={self.primary_provider_name}, fallback={'enabled' if self.enable_fallback else 'disabled'}")

    def _create_provider(self, provider_name: str) -> LlmProviderPort:
        """
        Create LLM provider instance

        Args:
            provider_name: Provider name ('openai' or 'together')

        Returns:
            LLM provider instance
        """
        if provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "together":
            return TogetherProvider()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text with automatic fallback support

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Randomness (0-2)
            max_tokens: Maximum response length

        Returns:
            Generated text
        """
        # Try primary provider with retries
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Attempting {self.current_provider_name} (attempt {attempt + 1}/{self.max_retries})")

                result = await self.current_provider.generate_text(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                # Success! If we were using fallback, try to reset to primary
                if self.current_provider_name != self.primary_provider_name:
                    logger.info(f"Successfully used fallback provider: {self.current_provider_name}")

                return result

            except Exception as e:
                logger.warning(f"{self.current_provider_name} failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")

                # If this was the last retry
                if attempt == self.max_retries - 1:
                    # Try fallback if enabled and we haven't tried it yet
                    if self.enable_fallback and self.current_provider_name == self.primary_provider_name:
                        logger.warning(f"Primary provider {self.primary_provider_name} failed after {self.max_retries} attempts. Switching to fallback: {self.fallback_provider_name}")

                        # Switch to fallback
                        self.current_provider = self.fallback_provider
                        self.current_provider_name = self.fallback_provider_name

                        # Try fallback provider
                        try:
                            result = await self.fallback_provider.generate_text(
                                prompt=prompt,
                                system_prompt=system_prompt,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )

                            logger.info(f"✅ Fallback to {self.fallback_provider_name} successful!")
                            return result

                        except Exception as fallback_error:
                            logger.error(f"Fallback provider {self.fallback_provider_name} also failed: {str(fallback_error)}")
                            raise RuntimeError(
                                f"Both primary ({self.primary_provider_name}) and fallback ({self.fallback_provider_name}) providers failed. "
                                f"Primary error: {str(e)}, Fallback error: {str(fallback_error)}"
                            )
                    else:
                        # No fallback available or already tried fallback
                        raise RuntimeError(f"LLM generation failed after {self.max_retries} attempts: {str(e)}")

                # Wait before retry
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        raise RuntimeError("LLM generation failed: max retries exceeded")

    def reset_to_primary(self):
        """Reset to using primary provider"""
        self.current_provider = self.primary_provider
        self.current_provider_name = self.primary_provider_name
        logger.info(f"Reset to primary provider: {self.primary_provider_name}")

    def get_current_provider(self) -> str:
        """Get name of currently active provider"""
        return self.current_provider_name
