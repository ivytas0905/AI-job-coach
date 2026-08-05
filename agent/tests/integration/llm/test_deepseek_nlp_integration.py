import json

import httpx

from agent_service.infra.llm.providers import DeepSeekProvider
from agent_service.infra.nlp.section_extractor import SectionExtractor


async def test_deepseek_provider_drives_resume_extraction():
    async def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["role"] == "user"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "content": '{"personal_info":{"name":"Ada"},"experiences":[],"education":[],"skills":[]}'
                        },
                    }
                ],
                "usage": {"total_tokens": 10},
            },
        )

    provider = DeepSeekProvider(
        "secret",
        "deepseek-chat",
        "https://example.test",
        transport=httpx.MockTransport(handler),
    )
    extractor = SectionExtractor(provider)
    extracted = object()
    extractor._create_resume_from_json = lambda data, raw_text: extracted
    try:
        resume = await extractor.extract_resume_data("Ada Resume")
    finally:
        await provider.close()

    assert resume is extracted
