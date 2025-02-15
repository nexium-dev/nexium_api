from typing import get_type_hints

from fastapi import APIRouter
from starlette.requests import Request as StarletteRequest

from nexium_api.request.base_auth import BaseRequestAuth
from nexium_api.request.process_request import process_request
from nexium_api.request.request import Request as BaseRequest
from nexium_api.response.response import Response as BaseResponse


class BaseRouter:
    prefix: str = ''
    request_auth = BaseRequestAuth

    def __init__(self, prefix: str = ''):
        self.fastapi = APIRouter(prefix=self.prefix)
        self.prefix = prefix + self.prefix

        # Init child Routers
        for attr_name, attr in get_type_hints(self.__class__).items():
            if not issubclass(attr, BaseRouter):
               continue

            child_router = attr(prefix=self.prefix)
            setattr(self, attr_name, child_router)
            self.fastapi.include_router(child_router.fastapi)

        # Child routes
        # noinspection PyUnresolvedReferences
        self.routes = [
            self.__getattribute__(name)
            for name in dir(self)
            if hasattr(self.__getattribute__(name), '__wrapped__') and self.__getattribute__(name).__name__
        ]

        # Init child routes
        for route in self.routes:
            path, type_, func, request_data, response_data, request_auth, check_request_auth, kwargs = route.params
            request_auth = request_auth if request_auth else self.request_auth

            class Request(BaseRequest):
                auth: request_auth
                data: request_data

            class Response(BaseResponse):
                data: response_data

            @self.fastapi.post(
                path=path,
                response_model=Response,
                **kwargs,
            )
            async def route(request: Request, starlette_request: StarletteRequest):
                return await process_request(
                    request=request,
                    starlette_request=starlette_request,
                    func=func,
                )
