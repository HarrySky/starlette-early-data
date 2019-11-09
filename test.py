import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from starlette_early_data import EarlyDataMiddleware, deny_early_data


async def home(request: Request) -> PlainTextResponse:
    return PlainTextResponse("Always OK if deny_all=False")


@deny_early_data
async def security_risk(request: Request) -> PlainTextResponse:
    return PlainTextResponse("Security action done after handshake")


APP = Starlette(
    routes=[
        Route("/", home, methods=["GET"]),
        Route("/security_risk", security_risk, methods=["GET"]),
    ],
    middleware=[Middleware(EarlyDataMiddleware, {"deny_all": False}),],
)

if __name__ == "__main__":
    uvicorn.run(APP, host="0.0.0.0", port=8080)
