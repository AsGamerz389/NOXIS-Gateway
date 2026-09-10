from app.providers.base import ProviderAdapter


class GPT3Adapter(ProviderAdapter):
    provider_name = "gpt3"
    upstream_path = "/api/gpt3"
    query_param = "q"
