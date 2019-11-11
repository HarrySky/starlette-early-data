# starlette-early-data

Middleware and decorator for processing TLSv1.3 early data requests in Starlette

[![PyPI: starlette-early-data](https://img.shields.io/pypi/v/starlette-early-data)](https://pypi.org/project/starlette-early-data/)
[![Code Style: Black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)

Install: `pip install starlette-early-data`

## What this package can do:
- Detect if request is early data and mark it (`request.state.early_data = True`)
- Deny all early data requests (pass `deny_all=True` to `add_middleware`)
- Deny early data requests to specific endpoints (use decorator `@deny_early_data`)

Example:

```python
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
```

Send request to `http://127.0.0.1:8080/security_risk` with header `Early-Data=1` and you will get `425 Early Data`.

Request to `http://127.0.0.1:8080/` with the same header will only return `425 Early Data` if you pass `deny_all=True` to `app.add_middleware(...)`
