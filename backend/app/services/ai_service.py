import httpx
import json
from typing import AsyncGenerator, List, Dict, Any
from app.config import settings

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"


async def stream_claude_response(
    messages: List[Dict[str, str]],
    context: Dict[str, Any] = None
) -> AsyncGenerator[str, None]:
    system_message = "你是一个公务员考试备考助手，擅长行测和申论辅导。"
    if context:
        context_str = json.dumps(context, ensure_ascii=False)
        system_message += f"\n\n当前页面上下文: {context_str}"

    headers = {
        "x-api-key": settings.claude_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": settings.claude_model,
        "max_tokens": 4096,
        "system": system_message,
        "messages": messages,
        "stream": True,
    }

    async with httpx.AsyncClient() as client:
        async with client.stream("POST", CLAUDE_API_URL, headers=headers, json=payload, timeout=120) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        yield json.dumps({"delta": "", "done": True})
                        break
                    try:
                        event = json.loads(data)
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            if "text" in delta:
                                yield json.dumps({"delta": delta["text"], "done": False})
                    except json.JSONDecodeError:
                        continue
