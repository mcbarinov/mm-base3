from typing import Annotated

from litestar import Controller, get, post
from litestar.datastructures import Cookie
from litestar.response import Redirect, Template
from pydantic import BaseModel

from mm_base3.base_core import BaseCoreAny
from mm_base3.server.auth import ACCESS_TOKEN_NAME
from mm_base3.server.utils import render_html
from mm_base3.types_ import FormBody


class LoginForm(BaseModel):
    access_token: str


class AuthController(Controller):
    path = "/auth"
    tags = ["auth"]
    include_in_schema = False

    @get("/login", sync_to_thread=False)
    def login_page(self) -> Template:
        return render_html("login.j2")

    @post("/login", sync_to_thread=False)
    def login(self, core: BaseCoreAny, data: Annotated[LoginForm, FormBody]) -> Redirect:
        cookie = Cookie(
            key=ACCESS_TOKEN_NAME,
            value=data.access_token,
            domain=core.app_config.domain,
            httponly=True,
            max_age=60 * 60 * 24 * 30,
        )
        return Redirect(path="/", cookies=[cookie])

    @get("/logout", sync_to_thread=False)
    def logout(self) -> Redirect:
        return Redirect(path="/auth/login", cookies=[Cookie(key=ACCESS_TOKEN_NAME, value="")])
