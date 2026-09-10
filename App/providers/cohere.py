from app.providers.base import ProviderAdapter


class CohereAdapter(ProviderAdapter):
    provider_name = "cohere"
    upstream_path = "/api/cohere"
    query_param = "q"
