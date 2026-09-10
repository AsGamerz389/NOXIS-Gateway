from app.providers.base import ProviderAdapter


class GPTLogicAdapter(ProviderAdapter):
    provider_name = "gptlogic"
    upstream_path = "/api/gptlogic"
    query_param = "q"
    extra_params = {"prompt": "be+friendly"}

    def build_params(self, text: str) -> dict[str, str]:
        return {"q": text, "prompt": "be+friendly"}
