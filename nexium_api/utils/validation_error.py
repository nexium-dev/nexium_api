from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from nexium_api.response import ResponseError, Response, ResponseState


async def valudation_error_exception_handler(_: Request, exc: RequestValidationError):
    error = ResponseError(
        name='validation_error',
        class_name='ApiError',
        message='validation_error',
        data={'errors': exc.errors()},
    )
    response = Response(
        state=ResponseState.ERROR,
        error=error,
    )

    return ORJSONResponse(content=response.model_dump())
