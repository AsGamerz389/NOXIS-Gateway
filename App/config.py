import os
from dotenv import load_dotenv

load_dotenv()

NOXIS_API_KEYS: list[str] = [
    k.strip() for k in os.getenv("NOXIS_API_KEYS", "").split(",") if k.strip()
]
CORS_ORIGINS: list[str] = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()
]
UPSTREAM_TIMEOUT: int = int(os.getenv("UPSTREAM_TIMEOUT", "45"))
MAX_PROVIDER_ATTEMPTS: int = int(os.getenv("MAX_PROVIDER_ATTEMPTS", "3"))
DAS_APIA_BASE: str = os.getenv("DAS_APIA_BASE", "https://das-apia.netlify.app")

FALLBACK_ORDER: list[str] = [
    "deepseek-v3",
    "deepseek-r1",
    "qwen",
    "gemini",
    "llama-meta",
    "cohere",
    "gpt3",
    "gptlogic",
    "copilot",
]
