from collections.abc import Callable
from contextvars import ContextVar

from fastapi.responses import ORJSONResponse
from starlette.requests import Request as StarletteRequest

from nexium_api.request import Request
from nexium_api.response import Response, ResponseState, ResponseError
from nexium_api.utils import get_ip, APIError


ip: ContextVar[str] = ContextVar('ip')
country: ContextVar[str] = ContextVar('country')
city: ContextVar[str] = ContextVar('city')


async def process_request(
    request: Request,
    starlette_request: StarletteRequest,
    func: Callable,
    auth_checkers: dict[str, Callable],
) -> ORJSONResponse:
    try:
        # Localization
        ip.set(await get_ip(starlette_request=starlette_request))
        country.set('Arstotzka')
        city.set('Altan')

        # Auth
        # noinspection PyProtectedMember
        auth_checker = auth_checkers.get(request.auth._checker, None)
        if auth_checker:
            await auth_checker(auth=request.auth)

        # Process
        data = await func(**request.data.model_dump())
        response = Response(data=data)

    except APIError as e:
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
