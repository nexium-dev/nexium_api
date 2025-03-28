import logging
from functools import wraps
from typing import Type, Optional

from aiohttp import ClientSession

from nexium_api.response.state import ResponseState
from nexium_api.utils.api_error import APIError
from nexium_api.request.request import Request as BaseRequest
from nexium_api.response.response import Response as BaseResponse
from nexium_api.request.base_auth import BaseAuth
from nexium_api.request.base_data import BaseRequestData
from nexium_api.response.base_data import BaseResponseData


def route(
    request_data: Type[BaseRequestData],
    response_data: Type[BaseResponseData],
    path: str = '/',
    type_: str = 'POST',
    auth: Type[BaseAuth] = None,
    response_field: str = None,
    **kwargs_decorator,
):
    def decorator(f):
        f.params = (path, type_, f.__name__, request_data, response_data, auth, kwargs_decorator)

        @wraps(f)
        async def wrapper(cls, **kwargs):
            ra = auth if auth else cls.auth
            rd = request_data

            class Request(BaseRequest):
                auth: ra
                data: rd

            class Response(BaseResponse):
                data: Optional[response_data]

            url = cls.prefix + path
            json = Request(auth=cls.auth, data=request_data(**kwargs)).model_dump()

            async with ClientSession() as session:
                async with session.post(url=url, json=json) as response:
                    response_status = response.status
                    if response.status == 200:
                        response_json = await response.json()
                        response = Response(**response_json)

                        if response.state == ResponseState.ERROR:
                            error_class = next((c for c in cls.errors if c.__name__ == response.error.class_name), None)
                            if not error_class:
                                raise APIError()
                            raise error_class(message=response.error.message, **response.error.data)

                        if not response_field:
                            return response.data

                        return getattr(response.data, response_field)
                    else:
                        logging.error(response)
                        raise APIError(message=str(response.text), status=response_status)

        return wrapper
    return decorator
