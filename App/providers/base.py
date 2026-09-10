import time
import uuid
import logging
from abc import ABC, abstractmethod

import httpx

from app.config import DAS_APIA_BASE, UPSTREAM_TIMEOUT
from app.normalizer import normalize_response, normalize_image_response

logger = logging.getLogger("noxis")


class ProviderAdapter(ABC):
    provider_name: str = ""
    upstream_path: str = ""
    query_param: str = "q"
    extra_params: dict[str, str] = {}

    @property
    def base_url(self) -> str:
        return DAS_APIA_BASE

    def build_params(self, text: str) -> dict[str, str]:
        params = {self.query_param: text}
        params.update(self.extra_params)
        return params

    async def call(self, text: str) -> dict:
        url = f"{self.base_url}{self.upstream_path}"
        params = self.build_params(text)

        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT) as client:
                resp = await client.get(url, params=params)
                elapsed = time.monotonic() - start

                logger.info(
                    "provider=%s status=%d latency=%.2fs",
                    self.provider_name,
                    resp.status_code,
                    elapsed,
                )

                if resp.status_code == 404:
                    raise UpstreamError(self.provider_name, "Provider not found", 404)
                if resp.status_code == 429:
                    raise UpstreamError(self.provider_name, "Rate limited", 429)
                if resp.status_code >= 500:
                    raise UpstreamError(
                        self.provider_name,
                        f"Upstream error {resp.status_code}",
                        resp.status_code,
                    )
                if resp.status_code != 200:
                    raise UpstreamError(
                        self.provider_name,
                        f"HTTP {resp.status_code}",
                        resp.status_code,
                    )

                try:
                    raw = resp.json()
                except Exception:
                    raw = resp.text

                content, extra = normalize_response(raw)
                return {
                    "content": content,
                    "extra": extra,
                    "status_code": resp.status_code,
                }

        except httpx.TimeoutException:
            elapsed = time.monotonic() - start
            logger.warning("provider=%s timeout after %.2fs", self.provider_name, elapsed)
            raise UpstreamError(self.provider_name, "Request timed out", 504)
        except httpx.ConnectError as e:
            elapsed = time.monotonic() - start
            logger.warning(
                "provider=%s connection_error after %.2fs: %s",
                self.provider_name,
                elapsed,
                str(e),
            )
            raise UpstreamError(self.provider_name, "Connection failed", 502)
        except UpstreamError:
            raise
        except Exception as e:
            elapsed = time.monotonic() - start
            logger.error(
                "provider=%s unexpected_error after %.2fs: %s",
                self.provider_name,
                elapsed,
                str(e),
            )
            raise UpstreamError(self.provider_name, "Unexpected upstream error", 500)

    async def call_image(self, text: str) -> dict:
        url = f"{self.base_url}{self.upstream_path}"
        params = {self.query_param: text}

        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT) as client:
                resp = await client.get(url, params=params)
                elapsed = time.monotonic() - start

                logger.info(
                    "provider=%s image status=%d latency=%.2fs",
                    self.provider_name,
                    resp.status_code,
                    elapsed,
                )

                if resp.status_code != 200:
                    raise UpstreamError(
                        self.provider_name,
                        f"HTTP {resp.status_code}",
                        resp.status_code,
                    )

                try:
                    raw = resp.json()
                except Exception:
                    raw = resp.text

                image_url, extra = normalize_image_response(raw)
                return {
                    "image_url": image_url,
                    "extra": extra,
                    "status_code": resp.status_code,
                }

        except httpx.TimeoutException:
            raise UpstreamError(self.provider_name, "Request timed out", 504)
        except httpx.ConnectError as e:
            raise UpstreamError(self.provider_name, "Connection failed", 502)
        except UpstreamError:
            raise
        except Exception as e:
            raise UpstreamError(self.provider_name, "Unexpected upstream error", 500)

    def make_completion_id(self) -> str:
        return f"noxis-{uuid.uuid4().hex[:12]}"

    def make_timestamp(self) -> int:
        return int(time.time())


class UpstreamError(Exception):
    def __init__(self, provider: str, message: str, status_code: int = 500):
        self.provider = provider
        self.message = message
        self.status_code = status_code
        super().__init__(message)
