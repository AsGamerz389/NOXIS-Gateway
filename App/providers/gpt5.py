from app.providers.base import ProviderAdapter


class GPT5Adapter(ProviderAdapter):
    provider_name = "gpt-5"
    upstream_path = "/api/gpt-5"
    query_param = "q"
