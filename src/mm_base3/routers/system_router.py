from litestar import Controller, get
from litestar.response import Template

from mm_base3 import BaseCore, render_html


class SystemController(Controller):
    path = "/system"

    @get("/")
    def system_page(self, core: BaseCore) -> Template:
        stats = core.system_service.get_stats()
        return render_html("system.j2", stats=stats)
