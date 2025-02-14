from contextvars import ContextVar
from urllib.request import Request


request_context: ContextVar[Request] = ContextVar('request')
