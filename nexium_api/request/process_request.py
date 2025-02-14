from collections.abc import Callable

from fastapi.responses import ORJSONResponse
from starlette.requests import Request as StarletteRequest

from nexium_api.request import Request
from nexium_api.response import Response, ResponseState, ResponseError
from nexium_api.utils.api_error import ApiError


async def get_ip(starlette_request: StarletteRequest) -> str:
    x_forwarded_for = starlette_request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = starlette_request.client.host
    return ip


async def process_request(
    request: Request,
    starlette_request: StarletteRequest,
    func: Callable,
    check_request_auth: Callable,
) -> ORJSONResponse:
    try:
        if hasattr(func, '__self__'):
            cls = func.__self__.__class__
            cls.ip = await get_ip(starlette_request=starlette_request)
            cls.country, cls.city = 'Arstotzka', 'Altan'

        if check_request_auth:
            await check_request_auth(**request.auth.model_dump())

        data = await func(**request.data.model_dump())

        response = Response(data=data)
    except ApiError as e:
        response = Response(
            state=ResponseState.ERROR,
            error=ResponseError(
                name=e.name,
                calss_name=e.class_name,
                message=e.message,
                data=e.data,
            ),
        )

    return ORJSONResponse(content=response.model_dump())
