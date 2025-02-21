from typing import Any, Literal

from litestar import Controller, Request, Response, get
from mm_std import hr

from mm_base3 import BaseCore

type RequestAny = Request[Any, Any, Any]


class APIMethodController(Controller):
    path = "/"

    @get("/api-post/{url:path}", sync_to_thread=True)
    def post(self, core: BaseCore, url: str, request: RequestAny) -> Response[Any]:
        return self._api_method("POST", url, core.config.use_https, request)

    @get("/api-delete/{url:path}", sync_to_thread=True)
    def delete(self, core: BaseCore, url: str, request: RequestAny) -> Response[Any]:
        return self._api_method("DELETE", url, core.config.use_https, request)

    @staticmethod
    def _api_method(method: Literal["POST", "DELETE"], url: str, use_https: bool, request: RequestAny) -> Response[Any]:
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
        headers: dict[str, object] = {}  # {self.api_key_name: api_key}
        res = hr(url, method=method, headers=headers, params=dict(request.query_params), timeout=3)
        if res.content_type and res.content_type.startswith("text/plain"):
            return Response(res.body, media_type="text/plain")
        if res.json:
            return Response(res.json, media_type="application/json")
        return Response(res.body, media_type="text/plain")
