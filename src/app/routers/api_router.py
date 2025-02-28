from bson import ObjectId
from litestar import Controller, Router, delete, get, post
from mm_mongo import mongo_query
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from app.core import Core
from app.db import Data, DataStatus


class DataController(Controller):
    path = "/data"
    tags = ["data"]

    @get(sync_to_thread=True)
    def find_data(self, core: Core, status: DataStatus | None = None, limit: int = 100) -> list[Data]:
        return core.db.data.find(mongo_query(status=status), "-created_at", limit)

    @get("/exception", sync_to_thread=True)
    def raise_exception(self, core: Core) -> None:
        core.dlog("sdsd", core.dvalue.tmp3)
        raise ValueError("test exception")

    @post("/generate", sync_to_thread=True)
    def generate_data(self, core: Core) -> InsertOneResult:
        return core.data_service.generate_data()

    @get("/{id:str}", sync_to_thread=True)
    def get_data(self, core: Core, id: str) -> Data:
        return core.db.data.get(ObjectId(id))

    @post("/{id:str}/inc", sync_to_thread=True)
    def inc_data(self, core: Core, id: str, value: int | None = None) -> UpdateResult:
        return core.db.data.update(ObjectId(id), {"$inc": {"value": value or 1}})

    @delete("/{id:str}", status_code=200, sync_to_thread=True)
    def delete_data(self, core: Core, id: str) -> DeleteResult:
        return core.db.data.delete(ObjectId(id))


api_router = Router(path="/api", route_handlers=[DataController])
