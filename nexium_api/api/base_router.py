from typing import Callable

from fastapi import APIRouter
from starlette.requests import Request as StarletteRequest

from nexium_api.request.base_auth import BaseRequestAuth
from nexium_api.request.process_request import process_request
from nexium_api.request.request import Request as BaseRequest
from nexium_api.response.response import Response as BaseResponse


class BaseRouter:
    path: str = ''
    request_auth = BaseRequestAuth
    check_request_auth: Callable = None

    def __init__(self):
        super().__init__()

        # noinspection PyUnresolvedReferences
        self.routes = [
            self.__getattribute__(name)
            for name in dir(self)
            if hasattr(self.__getattribute__(name), '__wrapped__') and self.__getattribute__(name).__name__
        ]

        self.routers = [
            self.__getattribute__(name)
            for name in dir(self)
            if isinstance(self.__getattribute__(name), BaseRouter)
        ]

        self.fastapi_router = APIRouter(prefix=self.path)
        [self.fastapi_router.include_router(router.fastapi_router) for router in self.routers]

        for route in self.routes:
            path, type_, func, request_data, response_data, request_auth, check_request_auth, kwargs = route.params
            check_request_auth = check_request_auth if check_request_auth else self.check_request_auth
            request_auth = request_auth if request_auth else self.request_auth

            class Request(BaseRequest):
                auth: request_auth
                data: request_data

            class Response(BaseResponse):
                data: response_data

            @self.fastapi_router.post(
                path=path,
                response_model=Response,
                **kwargs,
            )
            async def route(request: Request, starlette_request: StarletteRequest):
                return await process_request(
                    check_request_auth=check_request_auth,
                    request=request,
                    starlette_request=starlette_request,
                    func=func,
                )
