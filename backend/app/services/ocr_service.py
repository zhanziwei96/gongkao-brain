import base64
import json
import os
from typing import Optional

import fitz  # PyMuPDF
from anthropic import AsyncAnthropic
from app.config import settings

PROMPT = """你是一个公务员考试行测题目解析助手。
请从提供的内容中提取以下信息，并只返回合法的 JSON 对象，不要包含任何其他文字：

{
  "question_text": "题目文字内容",
  "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"},
  "correct_answer": "A/B/C/D 或 空字符串",
  "question_type": "政治理论/常识判断/言语理解/数量关系/判断推理/资料分析 或 空字符串",
  "difficulty": 3
}

规则：
- 如果正确答案在内容中标注了（如【答案】C），请提取
- 如果题型能从内容判断，请匹配六个模块之一
- 如果某项无法确定，使用空字符串或默认值
- 只输出 JSON，不要 markdown 代码块
"""


def _get_client():
    cfg = settings.get_llm_config()
    return AsyncAnthropic(api_key=cfg["api_key"], base_url=cfg["base_url"])


def _get_model():
    cfg = settings.get_llm_config()
    return cfg["model"]


def _extract_json(text: str) -> dict:
    """从 LLM 返回的文本中提取 JSON"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            data = json.loads(text[start : end + 1])
        else:
            raise ValueError("无法解析 LLM 返回的 JSON")

    return {
        "question_text": data.get("question_text", ""),
        "options": data.get("options", {"A": "", "B": "", "C": "", "D": ""}),
        "correct_answer": data.get("correct_answer", ""),
        "question_type": data.get("question_type", ""),
        "difficulty": data.get("difficulty", 3),
    }


async def parse_image(file_path: str) -> dict:
    """使用 LLM Vision 解析图片中的题目"""
    cfg = settings.get_llm_config()
    if not cfg["api_key"]:
        raise ValueError("未配置 LLM API Key")

    ext = os.path.splitext(file_path)[1].lower()
    media_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")

    with open(file_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    client = _get_client()
    model = _get_model()

    # Anthropic 兼容的多模态格式
    response = await client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )

    text = response.content[0].text if response.content else ""
    return _extract_json(text)


async def parse_pdf(file_path: str) -> dict:
    """提取 PDF 文字后使用 LLM 解析题目"""
    cfg = settings.get_llm_config()
    if not cfg["api_key"]:
        raise ValueError("未配置 LLM API Key")

    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    if not text.strip():
        raise ValueError("PDF 中未能提取到文字")

    client = _get_client()
    model = _get_model()

    response = await client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"{PROMPT}\n\n---\n\nPDF 提取内容：\n{text}",
            }
        ],
    )

    result_text = response.content[0].text if response.content else ""
    return _extract_json(result_text)
