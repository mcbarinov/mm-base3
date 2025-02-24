from logging import Logger

from bson import ObjectId
from pymongo.results import DeleteResult

from mm_base3.base_db import BaseDb, DLog


class DLogService:
    def __init__(self, db: BaseDb, logger: Logger) -> None:
        self.db = db
        self.logger = logger

    def dlog(self, category: str, data: object = None) -> None:
        self.logger.debug("system_log %s %s", category, data)
        self.db.dlog.insert_one(DLog(id=ObjectId(), category=category, data=data))

    def get_system_logs(self, limit: int) -> list[DLog]:
        return self.db.dlog.find({}, "-created_at", limit)

    def get_system_log(self, id: ObjectId) -> DLog:
        return self.db.dlog.get(id)

    def delete_system_log(self, id: ObjectId) -> DeleteResult:
        return self.db.dlog.delete(id)
