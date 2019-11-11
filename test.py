from asynctest import TestCase, main
from starlette import status
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from httpx import AsyncClient
from starlette_early_data import EarlyDataMiddleware, deny_early_data


async def home(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


@deny_early_data
async def security_risk(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


ROUTES = [
    Route("/", endpoint=home, methods=["GET"]),
    Route("/security_risk", endpoint=security_risk, methods=["GET"]),
]

DEFAULT = Starlette(routes=ROUTES, middleware=[Middleware(EarlyDataMiddleware),],)
DENY_ALL = Starlette(
    routes=ROUTES,
    middleware=[Middleware(EarlyDataMiddleware, options={"deny_all": True}),],
)


class StarletteEarlyDataTest(TestCase):
    async def test_behaviour_without_early_data(self) -> None:
        async with AsyncClient(app=DEFAULT, base_url="http://test") as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = await client.get("http://test/security_risk")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        async with AsyncClient(app=DENY_ALL, base_url="http://test") as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = await client.get("http://test/security_risk")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    async def test_deny_all_app(self) -> None:
        async with AsyncClient(
            app=DENY_ALL, base_url="http://test", headers={"Early-Data": "1"}
        ) as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_425_TOO_EARLY)
            response = await client.get("http://test/security_risk")
            self.assertEqual(response.status_code, status.HTTP_425_TOO_EARLY)

    async def test_default_app(self) -> None:
        async with AsyncClient(
            app=DEFAULT, base_url="http://test", headers={"Early-Data": "1"}
        ) as client:
            response = await client.get("http://test/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = await client.get("http://test/security_risk")
            self.assertEqual(response.status_code, status.HTTP_425_TOO_EARLY)


if __name__ == "__main__":
    main()
