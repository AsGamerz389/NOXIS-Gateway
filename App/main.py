import time
import logging

from fastapi import FastAPI, Query, Request, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.auth import verify_api_key
from app.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatMessage,
    ImageGenerationRequest,
    ModelInfo,
    ModelListResponse,
    ErrorResponse,
    ErrorDetail,
    dump,
)
from app.router import (
    ALL_MODEL_NAMES,
    get_provider,
    extract_user_text,
    route_chat,
    route_chat_auto,
    route_image,
)
from app.providers.base import UpstreamError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("noxis")

app = FastAPI(title="N?XIS API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def error_response(message: str, err_type: str, code: str, status: int, provider: str | None = None):
    detail = ErrorDetail(message=message, type=err_type, code=code, provider=provider)
    return JSONResponse(status_code=status, content=dump(ErrorResponse(error=detail)))


@app.get("/")
async def root():
    return FileResponse("web/index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "noxis-gateway"}


@app.get("/v1/models")
async def list_models(_key: str | None = Depends(verify_api_key)):
    data = [ModelInfo(id=name) for name in ALL_MODEL_NAMES]
    return dump(ModelListResponse(data=data))


@app.post("/v1/chat/completions")
async def chat_completions(
    req: ChatCompletionRequest,
    _key: str | None = Depends(verify_api_key),
):
    if req.stream:
        return error_response(
            "Streaming is not supported by this upstream provider",
            "invalid_request_error",
            "STREAMING_UNSUPPORTED",
            400,
        )

    text = extract_user_text(req.messages)

    try:
        if req.model.lower() == "auto":
            result, used_provider = await route_chat_auto(text)
        else:
            provider = get_provider(req.model)
            if provider is None:
                return error_response(
                    "Unknown model/provider",
                    "invalid_request_error",
                    "MODEL_NOT_FOUND",
                    404,
                )
            used_provider = req.model
            result = await provider.call(text)
    except ValueError:
        return error_response(
            "Unknown model/provider",
            "invalid_request_error",
            "MODEL_NOT_FOUND",
            404,
        )
    except UpstreamError as e:
        status = e.status_code if e.status_code < 600 else 502
        return error_response(
            e.message,
            "service_unavailable",
            "NOXIS_UPSTREAM_ERROR",
            status,
            provider=e.provider,
        )

    provider = get_provider(used_provider)
    completion_id = provider.make_completion_id() if provider else f"noxis-{int(time.time())}"
    created = int(time.time())

    extra = result.get("extra", {})
    x_noxis = extra if extra else None

    response = ChatCompletionResponse(
        id=completion_id,
        created=created,
        model=req.model,
        choices=[
            ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=result.get("content", "")),
            )
        ],
        x_noxis=x_noxis,
    )
    return dump(response)


@app.post("/v1/images/generations")
async def image_generations(
    req: ImageGenerationRequest,
    _key: str | None = Depends(verify_api_key),
):
    try:
        result = await route_image("dall-e", req.prompt)
    except ValueError:
        return error_response(
            "Image generation unavailable",
            "invalid_request_error",
            "MODEL_NOT_FOUND",
            404,
        )
    except UpstreamError as e:
        status = e.status_code if e.status_code < 600 else 502
        return error_response(
            e.message,
            "service_unavailable",
            "NOXIS_UPSTREAM_ERROR",
            status,
            provider=e.provider,
        )

    image_url = result.get("image_url")
    extra = result.get("extra", {})

    if image_url:
        return {
            "created": int(time.time()),
            "data": [{"url": image_url, "revised_prompt": req.prompt}],
            "x_noxis": extra if extra else None,
        }

    return error_response(
        "Upstream did not return a valid image URL",
        "service_unavailable",
        "NOXIS_NO_IMAGE_URL",
        502,
        provider="dall-e",
    )


@app.get("/v1/detect")
async def detect(
    text: str = Query(..., description="Text to analyze"),
    _key: str | None = Depends(verify_api_key),
):
    try:
        result = await route_chat("ai-detector", text)
    except UpstreamError as e:
        status = e.status_code if e.status_code < 600 else 502
        return error_response(
            e.message,
            "service_unavailable",
            "NOXIS_UPSTREAM_ERROR",
            status,
            provider="ai-detector",
        )

    return {
        "object": "detection",
        "model": "ai-detector",
        "input": text,
        "result": result.get("content", ""),
        "x_noxis": result.get("extra") or None,
    }


@app.get("/v1/bible")
async def bible(
    query: str = Query(..., description="Bible query"),
    _key: str | None = Depends(verify_api_key),
):
    try:
        result = await route_chat("bible-ai", query)
    except UpstreamError as e:
        status = e.status_code if e.status_code < 600 else 502
        return error_response(
            e.message,
            "service_unavailable",
            "NOXIS_UPSTREAM_ERROR",
            status,
            provider="bible-ai",
        )

    return {
        "object": "bible",
        "model": "bible-ai",
        "query": query,
        "result": result.get("content", ""),
        "x_noxis": result.get("extra") or None,
    }
