from typing import Optional, Any

from sqlmodel import SQLModel, Field

from .error import ResponseError
from .state import ResponseState


class Response(SQLModel):
    state: ResponseState = Field(default=ResponseState.SUCCESS)
    error: Optional[ResponseError] = Field(default=None)
    data: Optional[Any] = Field(default=None)
