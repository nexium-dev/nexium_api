from typing import Type

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import RedirectResponse, FileResponse

from nexium_api.router.base_router import BaseRouter
from nexium_api.utils.validation_error import valudation_error_exception_handler


class NexiumAPI(FastAPI):
    def __init__(
        self,
        main_router: Type[BaseRouter],
        title: str = 'Nexium API',
        redirect_docs: bool = True,
        favicon_path: str = None,
        **kwargs,
    ):
        super().__init__(title=title, docs_url=None, redoc_url=None, **kwargs)
        self.add_exception_handler(
            exc_class_or_status_code=RequestValidationError,
            handler=valudation_error_exception_handler,  # type: ignore
        )
        self.include_router(main_router().fastapi)

        @self.get(path='/docs', include_in_schema=False)
        async def favicon():
            return get_swagger_ui_html(
                title=title,
                openapi_url='/openapi.json',
                swagger_favicon_url='/favicon.ico',
            )

        if redirect_docs:
            @self.get(path='/', include_in_schema=False)
            async def redirect_docs():
                return RedirectResponse(url='/docs')

        if favicon_path:
            @self.get(path='/favicon.ico', include_in_schema=False)
            async def favicon():
                return FileResponse(favicon_path)
