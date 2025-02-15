from starlette.requests import Request


async def get_ip(starlette_request: Request) -> str:
    x_forwarded_for = starlette_request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = starlette_request.client.host
    return ip
