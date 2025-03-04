from bson import ObjectId
from litestar import Controller, Router, delete, get
from pymongo.results import DeleteResult

from mm_base3.core.core import BaseCoreAny
from mm_base3.core.db import DLog, DValue
from mm_base3.core.system_service import Stats


class DConfigController(Controller):
    path = "dconfigs"

    @get("toml", sync_to_thread=True)
    def get_dconfigs_as_toml(self, core: BaseCoreAny) -> str:
        return core.system_service.export_dconfig_as_toml()


class DValueController(Controller):
    path = "dvalues"

    @get("toml", sync_to_thread=True)
    def get_dvalue_as_toml(self, core: BaseCoreAny) -> str:
        return core.system_service.export_dvalue_as_toml()

    @get("{key:str}/toml", sync_to_thread=True)
    def get_field_as_toml(self, core: BaseCoreAny, key: str) -> str:
        return core.system_service.export_dvalue_field_as_toml(key)

    @get("{key:str}/value", sync_to_thread=True)
    def get_value(self, core: BaseCoreAny, key: str) -> object:
        return core.system_service.get_dvalue_value(key)

    @get("{key:str}", sync_to_thread=True)
    def get_dvalue(self, core: BaseCoreAny, key: str) -> DValue:
        return core.db.dvalue.get(key)


class DLogController(Controller):
    path = "dlogs"

    @get("{id:str}", sync_to_thread=True)
    def get_dlog(self, core: BaseCoreAny, id: str) -> DLog:
        return core.db.dlog.get(ObjectId(id))

    @delete("{id:str}", status_code=200, sync_to_thread=True)
    def delete_dlog(self, core: BaseCoreAny, id: str) -> DeleteResult:
        return core.db.dlog.delete(ObjectId(id))


class SystemAPIController(Controller):
    @get("/stats", sync_to_thread=True)
    def get_stats(self, core: BaseCoreAny) -> Stats:
        return core.system_service.get_stats()

    @get("/logfile", sync_to_thread=True)
    def read_logfile(self, core: BaseCoreAny) -> str:
        return core.system_service.read_logfile()

    @delete("/logfile", sync_to_thread=True)
    def delete_logfile(self, core: BaseCoreAny) -> None:
        core.system_service.clean_logfile()


system_api_router = Router(
    path="/api/system",
    tags=["system"],
    route_handlers=[DLogController, DConfigController, DValueController, SystemAPIController],
)
