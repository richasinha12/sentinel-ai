"""Featherless AI — open-source model inference via OpenAI-compatible API."""
from __future__ import annotations
from openai import AsyncOpenAI
from backend.config import settings

# Featherless uses OpenAI-compatible API
_client = AsyncOpenAI(
    api_key=settings.FEATHERLESS_API_KEY,
    base_url=settings.FEATHERLESS_BASE_URL,
)

# Model routing: task → best open-source model on Featherless
MODEL_MAP = {
    "extraction": "mistralai/Mistral-7B-Instruct-v0.3",
    "classification": "meta-llama/Meta-Llama-3-8B-Instruct",
    "summarization": "Qwen/Qwen2-7B-Instruct",
    "risk_scoring": "microsoft/Phi-3-mini-4k-instruct",
}


async def featherless_infer(task: str, prompt: str, system: str = "") -> str:
    """Run inference on Featherless AI with task-appropriate open-source model."""
    model = MODEL_MAP.get(task, MODEL_MAP["summarization"])
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = await _client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1024,
        temperature=0.2,
    )
    return resp.choices[0].message.content, model
