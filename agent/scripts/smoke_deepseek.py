"""Opt-in credentialed DeepSeek text and tool-call smoke test."""

import asyncio

from agent_service.application.ports.llm import LlmMessage
from agent_service.config import Settings
from agent_service.infra.llm.registry import build_provider


async def main() -> None:
    settings = Settings()
    provider = build_provider(settings)
    try:
        text_result = await provider.complete(
            [LlmMessage("user", "Reply with exactly: smoke-ok")],
            temperature=0,
            max_tokens=16,
        )
        if not text_result.text:
            raise RuntimeError("DeepSeek text smoke returned no text")

        tool_result = await provider.complete(
            [LlmMessage("user", "Call check_resume with resume_id smoke-1")],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "check_resume",
                        "description": "Checks a resume during credential smoke testing",
                        "parameters": {
                            "type": "object",
                            "properties": {"resume_id": {"type": "string"}},
                            "required": ["resume_id"],
                        },
                    },
                }
            ],
            temperature=0,
            max_tokens=64,
        )
        if not tool_result.tool_requests:
            raise RuntimeError("DeepSeek tool smoke returned no tool call")
        print("DeepSeek credential smoke passed: text + tool call")
    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(main())
