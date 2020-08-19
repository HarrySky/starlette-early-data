from functools import wraps
from typing import Any, Awaitable, Callable

from starlette import status
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

__version__ = "1.1.0"
_too_early = PlainTextResponse("Too Early", status.HTTP_425_TOO_EARLY)


class EarlyDataMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette, deny_all: bool = False) -> None:
        super().__init__(app)
        self.deny_all = deny_all

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request.state.early_data = False
        if request.headers.get("Early-Data", None) == "1":
            if self.deny_all:
                return _too_early
            request.state.early_data = True
        response = await call_next(request)
        return response


def deny_early_data(
    endpoint: Callable[..., Awaitable[Any]]
) -> Callable[..., Awaitable[Any]]:
    @wraps(endpoint)
    async def endpoint_wrapper(request: Request, *args: Any, **kwargs: Any) -> Response:
        if request.state.early_data:
            return _too_early
        return await endpoint(request, *args, **kwargs)

    return endpoint_wrapper


__all__ = [
    "__version__",
    "EarlyDataMiddleware",
    "deny_early_data",
]
