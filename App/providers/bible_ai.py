from app.providers.base import ProviderAdapter


class BibleAIAdapter(ProviderAdapter):
    provider_name = "bible-ai"
    upstream_path = "/api/bible-ai"
    query_param = "q"
