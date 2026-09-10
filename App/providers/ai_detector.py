from app.providers.base import ProviderAdapter


class AIDetectorAdapter(ProviderAdapter):
    provider_name = "ai-detector"
    upstream_path = "/api/ai-detector"
    query_param = "q"
