from app.providers.base import ProviderAdapter


class DallEAdapter(ProviderAdapter):
    provider_name = "dall-e"
    upstream_path = "/api/dalle"
    query_param = "q"
