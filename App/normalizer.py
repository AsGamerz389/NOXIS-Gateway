import json
from typing import Any


FIELD_PRIORITY = [
    "response",
    "text",
    "answer",
    "content",
    "message",
    "result",
    "output",
]


def normalize_response(raw: Any) -> tuple[str, dict[str, Any]]:
    if raw is None:
        return "", {}

    if isinstance(raw, str):
        return raw.strip(), {}

    if isinstance(raw, (int, float, bool)):
        return str(raw), {}

    if isinstance(raw, dict):
        extra = {}
        for k, v in raw.items():
            if k not in FIELD_PRIORITY and k not in ("status", "success", "error"):
                extra[k] = v

        for field in FIELD_PRIORITY:
            if field in raw:
                val = raw[field]
                if isinstance(val, str):
                    return val.strip(), extra
                if isinstance(val, dict):
                    if "content" in val:
                        return str(val["content"]).strip(), extra
                    if "text" in val:
                        return str(val["text"]).strip(), extra
                    if "message" in val:
                        return str(val["message"]).strip(), extra
                    try:
                        return json.dumps(val, ensure_ascii=False), extra
                    except (TypeError, ValueError):
                        return str(val), extra
                if val is not None:
                    return str(val).strip(), extra

        try:
            return json.dumps(raw, ensure_ascii=False), extra
        except (TypeError, ValueError):
            return str(raw), extra

    if isinstance(raw, list):
        if len(raw) == 1:
            return normalize_response(raw[0])
        try:
            return json.dumps(raw, ensure_ascii=False), {}
        except (TypeError, ValueError):
            return str(raw), {}

    return str(raw).strip(), {}


def normalize_image_response(raw: Any) -> tuple[str | None, dict[str, Any]]:
    if raw is None:
        return None, {}

    if isinstance(raw, str):
        if raw.startswith("http"):
            return raw, {}
        return None, {"raw_response": raw}

    if isinstance(raw, dict):
        for key in ("url", "image_url", "image", "link", "output", "result", "response"):
            if key in raw:
                val = raw[key]
                if isinstance(val, str) and val.startswith("http"):
                    return val, {k: v for k, v in raw.items() if k != key}
                if isinstance(val, dict) and "url" in val:
                    return val["url"], {k: v for k, v in raw.items() if k != key}
        return None, raw

    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                url, _ = normalize_image_response(item)
                if url:
                    return url, {}
        return None, {"raw_response": raw}

    return None, {"raw_response": str(raw)}
