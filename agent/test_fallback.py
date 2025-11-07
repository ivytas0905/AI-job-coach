"""Test script for LLM fallback functionality"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_service.infra.llm import LLMManager
from agent_service.config import get_settings


async def test_fallback():
    """Test LLM fallback from OpenAI to Together AI"""

    print("=" * 60)
    print("Testing LLM Fallback System")
    print("=" * 60)

    settings = get_settings()

    print(f"\n📋 Configuration:")
    print(f"  Primary Provider: {settings.llm_provider}")
    print(f"  Fallback Provider: {settings.fallback_provider}")
    print(f"  Fallback Enabled: {settings.enable_fallback}")
    print(f"  Max Retries: {settings.max_retries}")
    print(f"  Retry Delay: {settings.retry_delay}s")

    # Initialize LLM Manager
    llm_manager = LLMManager()

    print(f"\n🚀 Testing with simple prompt...")

    try:
        # Simple test prompt
        prompt = "Say 'Hello, this is a test!' in one sentence."

        print(f"\n📤 Prompt: {prompt}")
        print(f"⏳ Generating response...")

        response = await llm_manager.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=50
        )

        print(f"\n✅ Success!")
        print(f"📥 Response: {response}")
        print(f"🔧 Provider used: {llm_manager.get_current_provider()}")

    except Exception as e:
        print(f"\n❌ Failed: {str(e)}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


async def test_with_invalid_openai_key():
    """Test fallback behavior when OpenAI key is invalid"""

    print("\n" + "=" * 60)
    print("Testing Fallback with Invalid OpenAI Key")
    print("=" * 60)

    # This test requires you to temporarily use an invalid OpenAI key
    # and a valid Together AI key in your .env file

    print("\n⚠️  To test fallback:")
    print("1. Temporarily set OPENAI_API_KEY to an invalid key in .env")
    print("2. Set TOGETHER_API_KEY to a valid key in .env")
    print("3. Run this test again")
    print("4. You should see it fail on OpenAI then succeed on Together AI")


if __name__ == "__main__":
    # Run basic test
    asyncio.run(test_fallback())

    # Show fallback instructions
    asyncio.run(test_with_invalid_openai_key())
