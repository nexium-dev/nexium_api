from typing import Optional, Any

from sqlmodel import SQLModel


class ResponseError(SQLModel):
    name: str
    class_name: str
    message: str
    data: Optional[Any]
