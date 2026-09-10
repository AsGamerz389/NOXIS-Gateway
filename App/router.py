import logging

from app.providers.base import UpstreamError
from app.providers.ai_detector import AIDetectorAdapter
from app.providers.gemini import GeminiAdapter
from app.providers.dalle import DallEAdapter
from app.providers.gpt3 import GPT3Adapter
from app.providers.bible_ai import BibleAIAdapter
from app.providers.deepseek_r1 import DeepSeekR1Adapter
from app.providers.deepseek_v3 import DeepSeekV3Adapter
from app.providers.cohere import CohereAdapter
from app.providers.llama_meta import LlamaMetaAdapter
from app.providers.qwen import QwenAdapter
from app.providers.gpt5 import GPT5Adapter
from app.providers.deep_ai import DeepAIAdapter
from app.providers.gptlogic import GPTLogicAdapter
from app.providers.copilot import CopilotAdapter
from app.config import MAX_PROVIDER_ATTEMPTS, FALLBACK_ORDER

logger = logging.getLogger("noxis")

PROVIDERS: dict[str, type] = {
    "ai-detector": AIDetectorAdapter,
    "ai_detector": AIDetectorAdapter,
    "gemini": GeminiAdapter,
    "dall-e": DallEAdapter,
    "dall_e": DallEAdapter,
    "gpt3": GPT3Adapter,
    "gpt-3": GPT3Adapter,
    "bible-ai": BibleAIAdapter,
    "bible_ai": BibleAIAdapter,
    "deepseek-r1": DeepSeekR1Adapter,
    "deepseek_r1": DeepSeekR1Adapter,
    "deepseek-v3": DeepSeekV3Adapter,
    "deepseek_v3": DeepSeekV3Adapter,
    "cohere": CohereAdapter,
    "llama-meta": LlamaMetaAdapter,
    "llama_meta": LlamaMetaAdapter,
    "qwen": QwenAdapter,
    "gpt-5": GPT5Adapter,
    "gpt5": GPT5Adapter,
    "deep-ai": DeepAIAdapter,
    "deep_ai": DeepAIAdapter,
    "gptlogic": GPTLogicAdapter,
    "copilot": CopilotAdapter,
}

ALL_MODEL_NAMES: list[str] = [
    "ai-detector",
    "gemini",
    "dall-e",
    "gpt3",
    "bible-ai",
    "deepseek-r1",
    "deepseek-v3",
    "cohere",
    "llama-meta",
    "qwen",
    "gpt-5",
    "deep-ai",
    "gptlogic",
    "copilot",
]


def get_provider(model_name: str):
    adapter_cls = PROVIDERS.get(model_name.lower())
    if adapter_cls is None:
        return None
    return adapter_cls()


def extract_user_text(messages: list) -> str:
    if not messages:
        return ""
    parts = []
    for msg in messages:
        role = getattr(msg, "role", "user") if not isinstance(msg, dict) else msg.get("role", "user")
        content = getattr(msg, "content", "") if not isinstance(msg, dict) else msg.get("content", "")
        if content:
            parts.append(f"{role}: {content}")
    return "\n".join(parts)


async def route_chat(provider_name: str, text: str) -> dict:
    provider = get_provider(provider_name)
    if provider is None:
        raise ValueError("unknown_model")

    return await provider.call(text)


async def route_chat_auto(text: str) -> tuple[dict, str]:
    last_error = None
    for name in FALLBACK_ORDER[:MAX_PROVIDER_ATTEMPTS]:
        provider = get_provider(name)
        if provider is None:
            continue
        try:
            result = await provider.call(text)
            return result, name
        except UpstreamError as e:
            logger.warning("fallback: %s failed (%s), trying next", name, e.message)
            last_error = e
            continue

    if last_error:
        raise last_error
    raise UpstreamError("auto", "All fallback providers failed", 502)


async def route_image(provider_name: str, text: str) -> dict:
    provider = get_provider(provider_name)
    if provider is None:
        raise ValueError("unknown_model")
    return await provider.call_image(text)
