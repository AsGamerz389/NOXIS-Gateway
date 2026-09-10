from app.providers.base import ProviderAdapter


class CopilotAdapter(ProviderAdapter):
    provider_name = "copilot"
    upstream_path = "/api/copilot"
    query_param = "text"
