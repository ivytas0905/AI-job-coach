"""Vendor identities using the shared chat transport."""

from .chat_transport import ChatTransport


class DeepSeekProvider(ChatTransport):
    provider_name = "deepseek"


class OpenAIProvider(ChatTransport):
    provider_name = "openai"


class TogetherAIProvider(ChatTransport):
    provider_name = "togetherai"
