from typing import Annotated

from bson import ObjectId
from litestar import Controller, Router, delete, get, post
from litestar.response import Redirect, Template
from pymongo.results import DeleteResult

from mm_base3 import render_html
from mm_base3.base_core import BaseCoreAny
from mm_base3.base_db import DConfigType, DLog
from mm_base3.services.system_service import Stats
from mm_base3.types_ import FormBody


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

    @get("dconfig/toml")
    def dconfig_toml_page(self, core: BaseCoreAny) -> Template:
        toml_str = core.dconfig_service.export_dconfig_as_toml()
        return render_html("dconfig_toml.j2", toml_str=toml_str)

    @get("dconfig/multiline/{key:str}")
    def update_dconfig_multiline_page(self, core: BaseCoreAny, key: str) -> Template:
        dconfig = core.dconfig
        return render_html("dconfig_multiline.j2", dconfig=dconfig, key=key)

    @post("dconfig")
    def update_dconfig(self, core: BaseCoreAny, data: Annotated[dict[str, str], FormBody]) -> Redirect:
        """Update dconfig values  that are neither multiline nor hidden"""
        update_data = {
            x: data.get(x, "") for x in core.dconfig.get_non_hidden_keys() if core.dconfig.get_type(x) != DConfigType.MULTILINE
        }
        core.dconfig_service.update_dconfig_values(update_data)
        return Redirect(path="/system/dconfig")  # TODO: flash message

    @post("dconfig/multiline/{key:str}")
    def update_dconfig_multiline(self, core: BaseCoreAny, key: str, data: Annotated[dict[str, str], FormBody]) -> Redirect:
        core.dconfig_service.update_multiline(key, data["value"])
        return Redirect(path="/system/dconfig")  # TODO: flash message

    @post("dconfig/toml")
    def update_dconfig_from_toml(self, core: BaseCoreAny, data: Annotated[dict[str, str], FormBody]) -> Redirect:
        core.dconfig_service.update_dconfig_from_toml(data["value"])
        return Redirect(path="/system/dconfig")  # TODO: flash message


class DLogController(Controller):
    path = "/api/system/dlogs"

    @get("{id:str}")
    def get_dlog(self, core: BaseCoreAny, id: str) -> DLog:
        return core.db.dlog.get(ObjectId(id))

    @delete("{id:str}", status_code=200)
    def delete_dlog(self, core: BaseCoreAny, id: str) -> DeleteResult:
        return core.db.dlog.delete(ObjectId(id))


class DConfigController(Controller):
    path = "/api/system/dconfig"

    @get("toml")
    def get_dconfigs_as_toml(self, core: BaseCoreAny) -> str:
        return core.dconfig_service.export_dconfig_as_toml()


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


system_router = Router(path="/", route_handlers=[SystemUIController, DLogController, DConfigController, SystemAPIController])
