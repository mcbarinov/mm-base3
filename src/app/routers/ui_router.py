from litestar import Controller, Router, get
from litestar.response import Template

from app.core import Core
from mm_base3 import render_html


class PageController(Controller):
    path = "/"
    tags = ["ui"]

    @get()
    def index(self) -> Template:
        return render_html("index.j2")

    @get("/data")
    def t1(self, core: Core) -> Template:
        return render_html("data.j2", data_list=core.db.data.find({}))


class ActionController(Controller):
    path = "/"


ui_router = Router(path="/", tags=["ui"], route_handlers=[PageController, ActionController], include_in_schema=False)
