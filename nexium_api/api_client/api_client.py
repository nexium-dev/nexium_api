from typing import Type

from .protocol import Protocol
from nexium_api.request.base_auth import BaseAuth
from nexium_api.utils.api_error import APIError


class NexiumApiClient:
    def __init__(
        self,
        host: str,
        auth: BaseAuth = None,
        protocol: Protocol = Protocol.HTTPS,
        errors: list[Type[APIError]] = None,
        errors_module = None,
    ):
        self.host = host
        self.auth = auth
        self.protocol = protocol

        self.errors = errors if errors else []
        self.errors.append(APIError) if APIError not in self.errors else None
        if errors_module:
            self.errors += [
                cls
                for name, cls in vars(errors_module).items()
                if isinstance(cls, type)
                   and issubclass(cls, APIError)
                   and cls is not APIError
                   and cls not in self.errors
            ]

        # noinspection HttpUrlsUsage
        prefix = f'{"https://" if protocol == Protocol.HTTPS else "http://"}{self.host}'
        super().__init__(prefix=prefix, is_api_client=True, facade_services=[], auth=self.auth, errors=self.errors)
