from app.providers.base import ProviderAdapter


class GeminiAdapter(ProviderAdapter):
    provider_name = "gemini"
    upstream_path = "/api/gemini"
    query_param = "q"
