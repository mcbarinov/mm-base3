from litestar import Controller, Router, delete, get
from litestar.response import Template

from mm_base3 import BaseCore, render_html
from mm_base3.system_service import Stats


class SystemController(Controller):
    path = "/system"

    @get()
    def system_page(self, core: BaseCore) -> Template:
        stats = core.system_service.get_stats()
        return render_html("system.j2", stats=stats)


class SystemAPIController(Controller):
    path = "/api/system"

    @get("/stats")
    def get_stats(self, core: BaseCore) -> Stats:
        return core.system_service.get_stats()

    @get("/logfile")
    def read_logfile(self, core: BaseCore) -> str:
        return core.system_service.read_logfile()

    @delete("/logfile")
    def delete_logfile(self, core: BaseCore) -> None:
        core.system_service.clean_logfile()


system_router = Router(path="/", route_handlers=[SystemController, SystemAPIController])
