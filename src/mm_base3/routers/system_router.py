from bson import ObjectId
from litestar import Controller, Router, delete, get
from litestar.response import Template
from pymongo.results import DeleteResult

from mm_base3 import BaseCore, render_html
from mm_base3.base_db import SystemLog
from mm_base3.system_service import Stats


class SystemController(Controller):
    path = "/system"

    @get()
    def system_page(self, core: BaseCore) -> Template:
        stats = core.system_service.get_stats()
        return render_html("system.j2", stats=stats)

    @get("system-logs")
    def system_logs_page(self, core: BaseCore) -> Template:
        system_logs = core.system_service.get_system_logs(100)
        return render_html("system_logs.j2", system_logs=system_logs)


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

    @get("/system-logs/{id:str}")
    def get_system_log(self, core: BaseCore, id: str) -> SystemLog:
        return core.system_service.get_system_log(ObjectId(id))

    @delete("/system-logs/{id:str}", status_code=200)
    def delete_system_log(self, core: BaseCore, id: str) -> DeleteResult:
        return core.system_service.delete_system_log(ObjectId(id))


system_router = Router(path="/", route_handlers=[SystemController, SystemAPIController])
