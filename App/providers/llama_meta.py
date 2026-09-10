from app.providers.base import ProviderAdapter


class LlamaMetaAdapter(ProviderAdapter):
    provider_name = "llama-meta"
    upstream_path = "/api/llama-meta"
    query_param = "q"
