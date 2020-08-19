from typing import Optional

from asynctest import TestCase, main
from fastapi import FastAPI, Query
from httpx import AsyncClient
from starlette import status
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from starlette_early_data import EarlyDataMiddleware, deny_early_data


async def home(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


@deny_early_data
async def security_risk(
    request: Request, test: Optional[int] = Query(None)
) -> PlainTextResponse:
    if isinstance(test, int):
        return PlainTextResponse(str(test))
    return PlainTextResponse("OK")


DEFAULT = Starlette(middleware=[Middleware(EarlyDataMiddleware)])
DEFAULT.add_route("/", home, methods=["GET"])
DEFAULT.add_route("/security_risk", security_risk, methods=["GET"])
DENY_ALL = Starlette(middleware=[Middleware(EarlyDataMiddleware, deny_all=True)])
DENY_ALL.add_route("/", home, methods=["GET"])
DENY_ALL.add_route("/security_risk", security_risk, methods=["GET"])


class StarletteEarlyDataTest(TestCase):
    async def test_behaviour_without_early_data(self) -> None:
        async with AsyncClient(app=DEFAULT, base_url="http://test") as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "OK")
            response = await client.get("http://test/security_risk")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "OK")

        async with AsyncClient(app=DENY_ALL, base_url="http://test") as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "OK")
            response = await client.get("http://test/security_risk")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "OK")

    async def test_deny_all_app(self) -> None:
        async with AsyncClient(
            app=DENY_ALL, base_url="http://test", headers={"Early-Data": "1"}
        ) as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_425_TOO_EARLY)
            self.assertEqual(response.text, "Too Early")
            response = await client.get("http://test/security_risk")
            self.assertEqual(response.status_code, status.HTTP_425_TOO_EARLY)
            self.assertEqual(response.text, "Too Early")

    async def test_default_app(self) -> None:
        async with AsyncClient(
            app=DEFAULT, base_url="http://test", headers={"Early-Data": "1"}
        ) as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "OK")
            response = await client.get("http://test/security_risk")
            self.assertEqual(response.status_code, status.HTTP_425_TOO_EARLY)
            self.assertEqual(response.text, "Too Early")


FASTAPI_DEFAULT = FastAPI(middleware=[Middleware(EarlyDataMiddleware)])
FASTAPI_DEFAULT.add_api_route("/", home, methods=["GET"])
FASTAPI_DEFAULT.add_api_route("/security_risk", security_risk, methods=["GET"])
FASTAPI_DENY_ALL = FastAPI(middleware=[Middleware(EarlyDataMiddleware, deny_all=True)])
FASTAPI_DENY_ALL.add_api_route("/", home, methods=["GET"])
FASTAPI_DENY_ALL.add_api_route("/security_risk", security_risk, methods=["GET"])


class FastAPIEarlyDataTest(TestCase):
    async def test_behaviour_without_early_data(self) -> None:
        async with AsyncClient(app=FASTAPI_DEFAULT, base_url="http://test") as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "OK")
            response = await client.get("http://test/security_risk?test=1")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "1")

        async with AsyncClient(app=FASTAPI_DENY_ALL, base_url="http://test") as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "OK")
            response = await client.get("http://test/security_risk?test=1")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "1")

    async def test_deny_all_app(self) -> None:
        async with AsyncClient(
            app=FASTAPI_DENY_ALL, base_url="http://test", headers={"Early-Data": "1"}
        ) as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_425_TOO_EARLY)
            self.assertEqual(response.text, "Too Early")
            response = await client.get("http://test/security_risk?test=1")
            self.assertEqual(response.status_code, status.HTTP_425_TOO_EARLY)
            self.assertEqual(response.text, "Too Early")

    async def test_default_app(self) -> None:
        async with AsyncClient(
            app=FASTAPI_DEFAULT, base_url="http://test", headers={"Early-Data": "1"}
        ) as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.text, "OK")
            response = await client.get("http://test/security_risk?test=1")
            self.assertEqual(response.status_code, status.HTTP_425_TOO_EARLY)
            self.assertEqual(response.text, "Too Early")


if __name__ == "__main__":
    main()
