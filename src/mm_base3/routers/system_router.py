from litestar import Controller, get
from litestar.response import Template

from mm_base3 import render_html


class SystemController(Controller):
    path = "/system"

    @get("/")
    def system_page(self) -> Template:
        return render_html("system.j2")
