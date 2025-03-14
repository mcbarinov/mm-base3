from typing import Any, Literal

from litestar import Controller, Response, get
from mm_std import hr

from mm_base3.server.auth import ACCESS_TOKEN_NAME
from mm_base3.server.config import BaseServerConfig
from mm_base3.server.types_ import RequestAny


class APIMethodController(Controller):
    path = "/"
    include_in_schema = False
    tags = ["api-method"]

    @get("/api-post/{url:path}", sync_to_thread=True)
    def post(self, server_config: BaseServerConfig, url: str, request: RequestAny) -> Response[Any]:
        return self._api_method("POST", url, server_config.use_https, server_config.access_token, request)

    @get("/api-delete/{url:path}", sync_to_thread=True)
    def delete(self, server_config: BaseServerConfig, url: str, request: RequestAny) -> Response[Any]:
        return self._api_method("DELETE", url, server_config.use_https, server_config.access_token, request)

    @staticmethod
    def _api_method(
        method: Literal["POST", "DELETE"], url: str, use_https: bool, access_token: str, request: RequestAny
    ) -> Response[Any]:
        base_url = str(request.base_url)
        if not base_url.endswith("/"):
            base_url = base_url + "/"
        url = url.removeprefix("/")
        url = base_url + "api/" + url
        if use_https:
            url = url.replace("http://", "https://", 1)
        if request.query_params:
            q = ""
            for k, v in request.query_params.items():
                q += f"{k}={v}&"
            url += f"?{q}"
        headers: dict[str, object] = {ACCESS_TOKEN_NAME: access_token}  # {self.api_key_name: api_key}
        res = hr(url, method=method, headers=headers, params=dict(request.query_params), timeout=3)
        if res.content_type and res.content_type.startswith("text/plain"):
            return Response(res.body, media_type="text/plain")
        if res.json:
            return Response(res.json, media_type="application/json")
        return Response(res.body, media_type="text/plain")
