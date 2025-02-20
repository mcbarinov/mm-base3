from litestar import Controller, get
from litestar.response import Template

from app.core import Core
from mm_base3.jinja import render_html


class UIController(Controller):
    path = "/"

    @get("/")
    def index(self) -> Template:
        return render_html("index.j2")

    @get("/data")
    def t1(self, core: Core) -> Template:
        return render_html("data.j2", data_list=core.db.data.find({}))
