from functools import wraps
from typing import Type, Callable

from nexium_api.request.base_data import BaseRequestData
from nexium_api.response.base_data import BaseResponseData


def route(
    request_data: Type[BaseRequestData],
    response_data: Type[BaseResponseData],
    func: Callable,
    path: str = '/',
    type_: str = 'POST',
    request_auth: BaseRequestData = None,
    check_request_auth: Callable = None,
    **kwargs_decorator,
):
    def decorator(f):
        f.params = (path, type_, func, request_data, response_data, request_auth, check_request_auth, kwargs_decorator)

        @wraps(f)
        async def wrapper(*args, **kwargs):
            pass

        return wrapper
    return decorator
