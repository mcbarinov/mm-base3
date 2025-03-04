from typing import Any

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult

from mm_base3.server.config import BaseServerConfig

ACCESS_TOKEN_NAME = "access-token"  # nosec: B105 # noqa: S105


class AuthMiddleware(AbstractAuthenticationMiddleware):
    async def authenticate_request(self, conn: ASGIConnection[Any, Any, Any, Any]) -> AuthenticationResult:
        if "core" not in conn.app.state:
            raise NotAuthorizedException
        server_config: BaseServerConfig = conn.app.state["server_config"]
        access_token = server_config.access_token
        if (
            conn.query_params.get(ACCESS_TOKEN_NAME) == access_token
            or conn.headers.get(ACCESS_TOKEN_NAME) == access_token
            or conn.cookies.get(ACCESS_TOKEN_NAME) == access_token
        ):
            return AuthenticationResult(user="user", auth="auth")

        raise NotAuthorizedException
