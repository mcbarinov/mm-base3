from typing import Any

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult

from mm_base3 import BaseCore

TOKEN_NAME = "access-token"  # noqa: S105


class AuthMiddleware(AbstractAuthenticationMiddleware):
    async def authenticate_request(self, conn: ASGIConnection[Any, Any, Any, Any]) -> AuthenticationResult:
        if "core" not in conn.app.state:
            raise NotAuthorizedException
        core: BaseCore = conn.app.state["core"]
        access_token = core.config.access_token
        if (
            conn.query_params.get(TOKEN_NAME) == access_token
            or conn.headers.get(TOKEN_NAME) == access_token
            or conn.cookies.get(TOKEN_NAME) == access_token
        ):
            return AuthenticationResult(user="user", auth="auth")

        raise NotAuthorizedException
