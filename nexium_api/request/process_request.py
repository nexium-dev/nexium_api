from collections.abc import Callable

from fastapi.responses import ORJSONResponse
from starlette.requests import Request as StarletteRequest

from nexium_api.request import Request
from nexium_api.response import Response, ResponseState, ResponseError
from nexium_api.utils import get_ip, ApiError


async def process_request(
    request: Request,
    starlette_request: StarletteRequest,
    func: Callable,
) -> ORJSONResponse:
    try:
        if hasattr(func, '__self__'):
            cls = func.__self__.__class__
            cls.ip = await get_ip(starlette_request=starlette_request)
            cls.country, cls.city = 'Arstotzka', 'Altan'

        await request.auth.check()

        data = await func(**request.data.model_dump())
        response = Response(data=data)

    except ApiError as e:
        response = Response(
            state=ResponseState.ERROR,
            error=ResponseError(
                name=e.name,
                class_name=e.class_name,
                message=e.message,
                data=e.data,
            ),
        )

    return ORJSONResponse(content=response.model_dump())
