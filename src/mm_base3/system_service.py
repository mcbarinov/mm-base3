from logging import Logger

from bson import ObjectId
from mm_mongo import DatabaseAny
from pydantic import BaseModel
from pymongo.results import DeleteResult

from mm_base3.base_db import BaseDb, SystemLog
from mm_base3.config import BaseConfig


class Stats(BaseModel):
    db: dict[str, int]  # collection name -> count
    logfile: int  # size in bytes
    system_log: int  # count


class SystemService:
    def __init__(self, config: BaseConfig, logger: Logger, database: DatabaseAny) -> None:
        self.logger = logger
        self.database = database
        self.db = BaseDb(database)
        self.logfile = config.data_dir / "app.log"

    def system_log(self, category: str, data: object = None) -> None:
        self.logger.debug("system_log %s %s", category, data)
        self.db.system_log.insert_one(SystemLog(id=ObjectId(), category=category, data=data))

    def get_stats(self) -> Stats:
        db_stats = {}
        for col in self.database.list_collection_names():
            db_stats[col] = self.database[col].estimated_document_count()
        return Stats(db=db_stats, logfile=self.logfile.stat().st_size, system_log=self.db.system_log.count({}))

    def read_logfile(self) -> str:
        return self.logfile.read_text(encoding="utf-8")

    def clean_logfile(self) -> None:
        self.logfile.write_text("")

    def get_system_logs(self, limit: int) -> list[SystemLog]:
        return self.db.system_log.find({}, "-created_at", limit)

    def get_system_log(self, id: ObjectId) -> SystemLog:
        return self.db.system_log.get(id)

    def delete_system_log(self, id: ObjectId) -> DeleteResult:
        return self.db.system_log.delete(id)
