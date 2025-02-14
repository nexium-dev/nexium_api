from typing import Optional, Any

from sqlmodel import SQLModel


class Request(SQLModel):
    auth: Optional[Any]
    data: Optional[Any]
