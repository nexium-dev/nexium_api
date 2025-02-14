from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import RedirectResponse, FileResponse

from .base_router import BaseRouter
from nexium_api.utils.validation_error import valudation_error_exception_handler


class NexiumAPI(BaseRouter):
    def get_fastapi(
        self,
        title: str = 'Nexium API',
        redirect_docs: bool = True,
        favicon_path: str = None,
        **kwargs,
    ):
        fastapi = FastAPI(
            title=title,
            docs_url=None,
            redoc_url=None,
            **kwargs,
        )
        fastapi.add_exception_handler(
            exc_class_or_status_code=RequestValidationError,
            handler=valudation_error_exception_handler,  # type: ignore
        )
        fastapi.include_router(self.fastapi_router)

        if redirect_docs:
            @fastapi.get(path='/', include_in_schema=False)
            async def redirect_docs():
                return RedirectResponse(url='/docs')

        if favicon_path:
            @fastapi.get(path='/favicon.ico', include_in_schema=False)
            async def favicon():
                return FileResponse(favicon_path)

        @fastapi.get(path='/docs', include_in_schema=False)
        async def favicon():
            return get_swagger_ui_html(
                title=title,
                openapi_url='/openapi.json',
                swagger_favicon_url='/favicon.ico',
            )
        return fastapi


