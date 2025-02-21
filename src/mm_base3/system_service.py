from logging import Logger

from bson import ObjectId
from mm_mongo import DatabaseAny
from pydantic import BaseModel

from mm_base3.base_db import BaseDb, SystemLog


class Stats(BaseModel):
    db: dict[str, int]  # collection name -> count


class SystemService:
    def __init__(self, logger: Logger, database: DatabaseAny) -> None:
        self.logger = logger
        self.database = database
        self.db = BaseDb(database)

    def system_log(self, category: str, data: object = None) -> None:
        self.logger.debug("system_log %s %s", category, data)
        self.db.system_log.insert_one(SystemLog(id=ObjectId(), category=category, data=data))

    def get_stats(self) -> Stats:
        db_stats = {}
        for col in self.database.list_collection_names():
            db_stats[col] = self.database[col].estimated_document_count()
        return Stats(db=db_stats)
