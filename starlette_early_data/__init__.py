from typing import Callable

from starlette import status
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

TOO_EARLY = PlainTextResponse("Too Early", status.HTTP_425_TOO_EARLY)


class EarlyDataMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Starlette, deny_all: bool = False):
        super().__init__(app)
        self.deny_all = deny_all

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request.state.early_data = False
        if request.headers.get("Early-Data", None) == "1":
            if self.deny_all:
                return TOO_EARLY

            request.state.early_data = True

        response = await call_next(request)

        return response


def deny_early_data(endpoint: Callable) -> Callable:
    async def endpoint_wrapper(request: Request) -> Response:
        if request.state.early_data:
            return TOO_EARLY

        return await endpoint(request)

    return endpoint_wrapper
