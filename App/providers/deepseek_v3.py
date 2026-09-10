from app.providers.base import ProviderAdapter


class DeepSeekV3Adapter(ProviderAdapter):
    provider_name = "deepseek-v3"
    upstream_path = "/api/deepseek-v3"
    query_param = "q"
