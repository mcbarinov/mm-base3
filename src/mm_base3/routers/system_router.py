from typing import Annotated

from bson import ObjectId
from litestar import Controller, Router, delete, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect, Template
from pymongo.results import DeleteResult

from mm_base3 import render_html
from mm_base3.base_core import BaseCoreAny
from mm_base3.base_db import DLog
from mm_base3.services.system_service import Stats


class SystemUIController(Controller):
    path = "/system"

    @get()
    def system_page(self, core: BaseCoreAny) -> Template:
        stats = core.system_service.get_stats()
        return render_html("system.j2", stats=stats)

    @get("dlogs")
    def dlogs_page(self, core: BaseCoreAny) -> Template:
        dlogs = core.db.dlog.find({}, "-created_at", 100)
        return render_html("dlogs.j2", dlogs=dlogs)

    @get("dconfig")
    def dconfig_page(self, core: BaseCoreAny) -> Template:
        dconfig = core.dconfig
        return render_html("dconfig.j2", dconfig=dconfig)

    @get("dconfig/multiline/{key:str}")
    def update_dconfig_multiline_page(self, core: BaseCoreAny, key: str) -> Template:
        dconfig = core.dconfig
        return render_html("dconfig_multiline.j2", dconfig=dconfig, key=key)

    @post("dconfig")
    def update_dconfig(
        self, core: BaseCoreAny, data: Annotated[dict[str, str], Body(media_type=RequestEncodingType.URL_ENCODED)]
    ) -> Redirect:
        core.dconfig_service.update(data)
        # TODO: flash message
        return Redirect(path="/system/dconfig")


class DLogController(Controller):
    path = "/api/system/dlogs"

    @get("{id:str}")
    def get_dlog(self, core: BaseCoreAny, id: str) -> DLog:
        return core.db.dlog.get(ObjectId(id))

    @delete("{id:str}", status_code=200)
    def delete_dlog(self, core: BaseCoreAny, id: str) -> DeleteResult:
        return core.db.dlog.delete(ObjectId(id))


class SystemAPIController(Controller):
    path = "/api/system"

    @get("/stats")
    def get_stats(self, core: BaseCoreAny) -> Stats:
        return core.system_service.get_stats()

    @get("/logfile")
    def read_logfile(self, core: BaseCoreAny) -> str:
        return core.system_service.read_logfile()

    @delete("/logfile")
    def delete_logfile(self, core: BaseCoreAny) -> None:
        core.system_service.clean_logfile()


system_router = Router(path="/", route_handlers=[SystemUIController, DLogController, SystemAPIController])
