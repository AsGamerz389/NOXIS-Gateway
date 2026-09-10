from app.providers.base import ProviderAdapter


class QwenAdapter(ProviderAdapter):
    provider_name = "qwen"
    upstream_path = "/api/qwen"
    query_param = "q"
