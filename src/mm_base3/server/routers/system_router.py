from typing import Annotated

from bson import ObjectId
from litestar import Controller, Router, delete, get, post
from litestar.plugins.flash import flash
from litestar.response import Redirect, Template
from pymongo.results import DeleteResult

from mm_base3 import render_html
from mm_base3.base_core import BaseCoreAny
from mm_base3.base_db import DConfigType, DLog, DValue
from mm_base3.dconfig import DConfigStorage
from mm_base3.dvalue import DValueStorage
from mm_base3.system_service import Stats
from mm_base3.types_ import FormBody, RequestAny


class SystemUIController(Controller):
    path = "/system"
    include_in_schema = False

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

    @get("dvalue")
    def dvalue_page(self, core: BaseCoreAny) -> Template:
        dvalue = core.dvalue
        return render_html("dvalue.j2", dvalue=dvalue)

    @get("dconfig/toml")
    def dconfig_toml_page(self) -> Template:
        return render_html("dconfig_toml.j2", toml_str=DConfigStorage.export_as_toml())

    @get("dconfig/multiline/{key:str}")
    def update_dconfig_multiline_page(self, core: BaseCoreAny, key: str) -> Template:
        dconfig = core.dconfig
        return render_html("dconfig_multiline.j2", dconfig=dconfig, key=key)

    @post("dconfig")
    def update_dconfig(self, core: BaseCoreAny, data: Annotated[dict[str, str], FormBody], request: RequestAny) -> Redirect:
        """Update dconfig values  that are neither multiline nor hidden"""
        update_data = {
            x: data.get(x, "") for x in core.dconfig.get_non_hidden_keys() if core.dconfig.get_type(x) != DConfigType.MULTILINE
        }
        DConfigStorage.update(update_data)
        flash(request, "dconfig updated successfully", "success")
        return Redirect(path="/system/dconfig")

    @post("dconfig/multiline/{key:str}")
    def update_dconfig_multiline(self, key: str, data: Annotated[dict[str, str], FormBody], request: RequestAny) -> Redirect:
        DConfigStorage.update_multiline(key, data["value"])
        flash(request, "dconfig updated successfully", "success")
        return Redirect(path="/system/dconfig")

    @post("dconfig/toml")
    def update_dconfig_from_toml(self, data: Annotated[dict[str, str], FormBody], request: RequestAny) -> Redirect:
        DConfigStorage.update_from_toml(data["value"])
        flash(request, "dconfig updated successfully", "success")
        return Redirect(path="/system/dconfig")


class DLogController(Controller):
    path = "/api/system/dlogs"

    @get("{id:str}")
    def get_dlog(self, core: BaseCoreAny, id: str) -> DLog:
        return core.db.dlog.get(ObjectId(id))

    @delete("{id:str}", status_code=200)
    def delete_dlog(self, core: BaseCoreAny, id: str) -> DeleteResult:
        return core.db.dlog.delete(ObjectId(id))


class DConfigController(Controller):
    path = "/api/system/dconfigs"

    @get("toml")
    def get_dconfigs_as_toml(self) -> str:
        return DConfigStorage.export_as_toml()


class DValueController(Controller):
    path = "/api/system/dvalues"

    @get("toml")
    def get_dvalue_as_toml(self) -> str:
        return DValueStorage.export_as_toml()

    @get("{key:str}/toml")
    def get_field_as_toml(self, key: str) -> str:
        return DValueStorage.export_field_as_toml(key)

    @get("{key:str}/value")
    def get_value(self, core: BaseCoreAny, key: str) -> object:
        return core.dvalue.get(key)

    @get("{key:str}")
    def get_dvalue(self, core: BaseCoreAny, key: str) -> DValue:
        return core.db.dvalue.get(key)


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


system_router = Router(
    path="/",
    tags=["system"],
    route_handlers=[SystemUIController, DLogController, DConfigController, DValueController, SystemAPIController],
)
