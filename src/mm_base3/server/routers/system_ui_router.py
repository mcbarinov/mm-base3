from typing import Annotated

from litestar import Controller, Router, get, post
from litestar.plugins.flash import flash
from litestar.response import Redirect, Template

from mm_base3.core.base_core import BaseCoreAny
from mm_base3.server import utils
from mm_base3.server.types_ import FormBody, RequestAny
from mm_base3.server.utils import render_html


class PagesController(Controller):
    @get(sync_to_thread=True)
    def system_page(self, core: BaseCoreAny) -> Template:
        stats = core.system_service.get_stats()
        return render_html("system.j2", stats=stats)

    @get("dlogs", sync_to_thread=True)
    def dlogs_page(self, core: BaseCoreAny) -> Template:
        dlogs = core.db.dlog.find({}, "-created_at", 100)
        return render_html("dlogs.j2", dlogs=dlogs)

    @get("dconfigs", sync_to_thread=False)
    def dconfig_page(self, core: BaseCoreAny) -> Template:
        info = core.system_service.get_dconfig_info()
        return render_html("dconfigs.j2", info=info)

    @get("dvalues", sync_to_thread=False)
    def dvalue_page(self, core: BaseCoreAny) -> Template:
        info = core.system_service.get_dvalue_info()
        return render_html("dvalues.j2", info=info)

    @get("dconfigs/toml", sync_to_thread=True)
    def dconfig_toml_page(self, core: BaseCoreAny) -> Template:
        return render_html("dconfigs_toml.j2", toml_str=core.system_service.export_dconfig_as_toml())

    @get("dconfigs/multiline/{key:str}", sync_to_thread=True)
    def update_dconfig_multiline_page(self, core: BaseCoreAny, key: str) -> Template:
        dconfig = core.dconfig
        return render_html("dconfigs_multiline.j2", dconfig=dconfig, key=key)


class ActionsController(Controller):
    @post("dconfigs", sync_to_thread=True)
    def update_dconfig(self, core: BaseCoreAny, data: Annotated[dict[str, object], FormBody], request: RequestAny) -> Redirect:
        core.system_service.update_dconfig(utils.process_form_with_checkboxes(data))
        flash(request, "dconfigs updated successfully", "success")
        return Redirect(path="/system/dconfigs")

    @post("dconfigs/multiline/{key:str}", sync_to_thread=True)
    def update_dconfig_multiline(
        self, core: BaseCoreAny, key: str, data: Annotated[dict[str, str], FormBody], request: RequestAny
    ) -> Redirect:
        core.system_service.update_dconfig({key: data["value"]})
        flash(request, "dconfig updated successfully", "success")
        return Redirect(path="/system/dconfigs")

    @post("dconfigs/toml", sync_to_thread=True)
    def update_dconfig_from_toml(
        self, core: BaseCoreAny, data: Annotated[dict[str, str], FormBody], request: RequestAny
    ) -> Redirect:
        core.system_service.update_dconfig_from_toml(data["value"])
        flash(request, "dconfigs updated successfully", "success")
        return Redirect(path="/system/dconfigs")


system_ui_router = Router(
    path="/system",
    include_in_schema=False,
    route_handlers=[PagesController, ActionsController],
)
