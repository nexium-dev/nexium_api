from sqlmodel import SQLModel


class BaseRequestAuth(SQLModel):
    async def check(self):
        pass
