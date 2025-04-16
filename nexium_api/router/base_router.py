from typing import get_type_hints, Type, Callable

from fastapi import APIRouter
from pydantic import PydanticSchemaGenerationError
from starlette.requests import Request as StarletteRequest

from nexium_api.utils.base_facade_service import BaseFacadeService
from nexium_api.utils.api_error import APIError
from nexium_api.request.base_auth import BaseAuth
from nexium_api.request.process_request import process_request
from nexium_api.request.request import Request as BaseRequest
from nexium_api.response.response import Response as BaseResponse


class BaseRouter:
    prefix: str = ''
    auth: BaseAuth = None
    facade_service: str = None

    def __init__(
        self,
        facade_services: list[Type[BaseFacadeService]],

        # Auth
        auth_checkers: dict[str, Callable] = None,
        auth: BaseAuth = BaseAuth,

        prefix: str = '',
        is_api_client: bool = False,
        errors: list[Type[APIError]] = None,
        is_main_router: bool = False,
    ):
        # For API Client
        self.auth = self.auth if self.auth else auth
        self.errors = errors

        # Tag
        tag = type(self).__mro__[0].__name__
        if not tag.endswith('Router') or is_main_router:
            tags = []
        else:
            tags = [tag[:-6]]

        self.fastapi = APIRouter(
            prefix=self.prefix,
            tags=tags,
        )
        self.prefix = prefix + self.prefix

        # Facade services
        self.facade_services = facade_services
        if self.facade_service and not is_api_client:
            self.facade_service_class = next((c for c in self.facade_services if c.__name__ == self.facade_service))
        else:
            self.facade_service_class = None


        # Init child Routers
        for attr_name, attr in get_type_hints(self.__class__).items():
            if not issubclass(attr, BaseRouter):
               continue

            child_router = attr(
                facade_services=self.facade_services,
                prefix=self.prefix,
                is_api_client=is_api_client,
                auth=self.auth,
                auth_checkers=auth_checkers,
                errors=self.errors,
            )
            setattr(self, attr_name, child_router)
            self.fastapi.include_router(child_router.fastapi)

        # Child routes
        self.routes = [
            self.__getattribute__(name)
            for name in dir(self)
            if hasattr(self.__getattribute__(name), '__wrapped__') and self.__getattribute__(name).__name__
        ]

        # Init child routes
        for route in self.routes:
            path, type_, func_name, request_data, response_data, auth, kwargs = route.params
            auth_ = auth if auth else self.auth

            # FIXME
            try:
                class Request(BaseRequest):
                    auth: auth_
                    data: request_data
            except PydanticSchemaGenerationError:
                from typing import Any
                class Request(BaseRequest):
                    auth: Any
                    data: request_data

            class Response(BaseResponse):
                data: response_data

            if is_api_client:
                continue

            if not self.facade_service_class:
                raise RuntimeError(f'Facade service for {self.__class__.__name__} is not specified')

            try:
                handler = self.facade_service_class().__getattribute__(func_name)
            except AttributeError:
                raise RuntimeError(f'{self.facade_service_class.__name__} does not have the "{func_name}" function')

            self.add_route(
                path=path,
                request=Request,
                response=Response,
                handler=handler,
                auth_checkers=auth_checkers,
            )

    def add_route(
        self,
        path: str,
        request: Type[BaseRequest],
        response: Type[BaseResponse],
        handler: Callable,
        auth_checkers: dict[str, Callable],
        **kwargs,
    ):
        async def endpoint(
            request_data: request,
            starlette_request: StarletteRequest,
        ):
            return await process_request(
                request=request_data,
                starlette_request=starlette_request,
                func=handler,
                auth_checkers=auth_checkers,
            )

        self.fastapi.post(path, response_model=response, **kwargs)(endpoint)
