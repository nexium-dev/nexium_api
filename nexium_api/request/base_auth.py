from typing import Optional

from pydantic import PrivateAttr
from sqlmodel import SQLModel


class BaseAuth(SQLModel):
    _checker: Optional[str] = PrivateAttr(default=None)
