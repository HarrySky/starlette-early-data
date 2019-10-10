import uvicorn

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from starlette_early_data import EarlyDataMiddleware, deny_early_data

app = Starlette()
app.add_middleware(EarlyDataMiddleware, deny_all=False)


@app.route("/")
async def home(request: Request) -> PlainTextResponse:
    return PlainTextResponse("Always OK if deny_all=False")


@app.route("/security_risk")
@deny_early_data
async def security_risk(request: Request) -> PlainTextResponse:
    return PlainTextResponse("Security action done after handshake")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
