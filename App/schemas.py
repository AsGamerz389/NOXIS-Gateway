from pydantic import BaseModel
from typing import Any


def dump(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


class ChatMessage(BaseModel):
    role: str = "user"
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage] = []
    stream: bool = False


class ImageGenerationRequest(BaseModel):
    prompt: str
    model: str = "dall-e"


class ChatChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatChoice]
    usage: dict[str, Any] = {}
    x_noxis: dict[str, Any] | None = None


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "noxis"


class ModelListResponse(BaseModel):
    object: str = "list"
    data: list[ModelInfo]


class ErrorDetail(BaseModel):
    message: str
    type: str
    code: str
    provider: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
