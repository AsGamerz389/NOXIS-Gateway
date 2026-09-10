from app.providers.base import ProviderAdapter


class DeepAIAdapter(ProviderAdapter):
    provider_name = "deep-ai"
    upstream_path = "/api/deep-ai"
    query_param = "query"
