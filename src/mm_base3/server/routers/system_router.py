from typing import Annotated

from bson import ObjectId
from litestar import Controller, Router, delete, get, post
from litestar.plugins.flash import flash
from litestar.response import Redirect, Template
from pymongo.results import DeleteResult

from mm_base3.core.base_core import BaseCoreAny
from mm_base3.core.base_db import DConfigType, DLog, DValue
from mm_base3.core.dconfig import DConfigStorage
from mm_base3.core.dvalue import DValueStorage
from mm_base3.core.system_service import Stats
from mm_base3.server.types_ import FormBody, RequestAny
from mm_base3.server.utils import render_html


class SystemUIController(Controller):
    path = "/system"
    include_in_schema = False

    @get(sync_to_thread=True)
    def system_page(self, core: BaseCoreAny) -> Template:
        stats = core.system_service.get_stats()
        return render_html("system.j2", stats=stats)

    @get("dlogs", sync_to_thread=True)
    def dlogs_page(self, core: BaseCoreAny) -> Template:
        dlogs = core.db.dlog.find({}, "-created_at", 100)
        return render_html("dlogs.j2", dlogs=dlogs)

    @get("dconfig", sync_to_thread=False)
    def dconfig_page(self, core: BaseCoreAny) -> Template:
        dconfig = core.dconfig
        hidden = DConfigStorage.hidden
        types = DConfigStorage.types
        return render_html("dconfig.j2", dconfig=dconfig, hidden=hidden, types=types)

    @get("dvalue", sync_to_thread=False)
    def dvalue_page(self, core: BaseCoreAny) -> Template:
        dvalue = core.dvalue
        return render_html("dvalue.j2", dvalue=dvalue)

    @get("dconfig/toml", sync_to_thread=True)
    def dconfig_toml_page(self) -> Template:
        return render_html("dconfig_toml.j2", toml_str=DConfigStorage.export_as_toml())

    @get("dconfig/multiline/{key:str}", sync_to_thread=True)
    def update_dconfig_multiline_page(self, core: BaseCoreAny, key: str) -> Template:
        dconfig = core.dconfig
        return render_html("dconfig_multiline.j2", dconfig=dconfig, key=key)

    @post("dconfig", sync_to_thread=True)
    def update_dconfig(self, data: Annotated[dict[str, str], FormBody], request: RequestAny) -> Redirect:
        """Update dconfig values  that are neither multiline nor hidden"""
        update_data = {
            x: data.get(x, "")
            for x in DConfigStorage.get_non_hidden_keys()
            if DConfigStorage.get_type(x) != DConfigType.MULTILINE
        }
        DConfigStorage.update(update_data)
        flash(request, "dconfig updated successfully", "success")
        return Redirect(path="/system/dconfig")

    @post("dconfig/multiline/{key:str}", sync_to_thread=True)
    def update_dconfig_multiline(self, key: str, data: Annotated[dict[str, str], FormBody], request: RequestAny) -> Redirect:
        DConfigStorage.update_multiline(key, data["value"])
        flash(request, "dconfig updated successfully", "success")
        return Redirect(path="/system/dconfig")

    @post("dconfig/toml", sync_to_thread=True)
    def update_dconfig_from_toml(self, data: Annotated[dict[str, str], FormBody], request: RequestAny) -> Redirect:
        DConfigStorage.update_from_toml(data["value"])
        flash(request, "dconfig updated successfully", "success")
        return Redirect(path="/system/dconfig")


class DLogController(Controller):
    path = "/api/system/dlogs"

    @get("{id:str}", sync_to_thread=True)
    def get_dlog(self, core: BaseCoreAny, id: str) -> DLog:
        return core.db.dlog.get(ObjectId(id))

    @delete("{id:str}", status_code=200, sync_to_thread=True)
    def delete_dlog(self, core: BaseCoreAny, id: str) -> DeleteResult:
        return core.db.dlog.delete(ObjectId(id))


class DConfigController(Controller):
    path = "/api/system/dconfig"

    @get("toml", sync_to_thread=True)
    def get_dconfigs_as_toml(self) -> str:
        return DConfigStorage.export_as_toml()


class DValueController(Controller):
    path = "/api/system/dvalues"

    @get("toml", sync_to_thread=True)
    def get_dvalue_as_toml(self) -> str:
        return DValueStorage.export_as_toml()

    @get("{key:str}/toml", sync_to_thread=True)
    def get_field_as_toml(self, key: str) -> str:
        return DValueStorage.export_field_as_toml(key)

    @get("{key:str}/value", sync_to_thread=True)
    def get_value(self, key: str) -> object:
        return DValueStorage.get_value(key)

    @get("{key:str}", sync_to_thread=True)
    def get_dvalue(self, core: BaseCoreAny, key: str) -> DValue:
        return core.db.dvalue.get(key)


class SystemAPIController(Controller):
    path = "/api/system"

    @get("/stats", sync_to_thread=True)
    def get_stats(self, core: BaseCoreAny) -> Stats:
        return core.system_service.get_stats()

    @get("/logfile", sync_to_thread=True)
    def read_logfile(self, core: BaseCoreAny) -> str:
        return core.system_service.read_logfile()

    @delete("/logfile", sync_to_thread=True)
    def delete_logfile(self, core: BaseCoreAny) -> None:
        core.system_service.clean_logfile()


system_router = Router(
    path="/",
    tags=["system"],
    route_handlers=[SystemUIController, DLogController, DConfigController, DValueController, SystemAPIController],
)
