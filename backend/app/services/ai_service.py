import json
from typing import AsyncGenerator, List, Dict, Any
from anthropic import AsyncAnthropic
from app.config import settings

SYSTEM_PROMPT = "你是一个公务员考试备考助手，擅长行测和申论辅导。"


def _get_client():
    cfg = settings.get_llm_config()
    return AsyncAnthropic(api_key=cfg["api_key"], base_url=cfg["base_url"])


def _get_model():
    cfg = settings.get_llm_config()
    return cfg["model"]


async def stream_claude_response(
    messages: List[Dict[str, str]],
    context: Dict[str, Any] = None
) -> AsyncGenerator[str, None]:
    system_message = SYSTEM_PROMPT
    if context:
        context_str = json.dumps(context, ensure_ascii=False)
        system_message += f"\n\n当前页面上下文: {context_str}"

    client = _get_client()
    model = _get_model()

    # Anthropic 格式：system 单独传入，messages 只含 user/assistant
    msgs = []
    for m in messages:
        if m["role"] == "system":
            continue
        msgs.append({"role": m["role"], "content": m["content"]})

    async with client.messages.stream(
        model=model,
        max_tokens=4096,
        system=system_message,
        messages=msgs,
    ) as stream:
        async for chunk in stream:
            if chunk.type == "text":
                yield json.dumps({"delta": chunk.text, "done": False})

    yield json.dumps({"delta": "", "done": True})
