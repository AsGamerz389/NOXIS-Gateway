from app.providers.base import ProviderAdapter


class DeepSeekR1Adapter(ProviderAdapter):
    provider_name = "deepseek-r1"
    upstream_path = "/api/deepseek-r1"
    query_param = "q"
