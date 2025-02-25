from logging import Logger

from pydantic import BaseModel

from mm_base3.base_db import BaseDb
from mm_base3.config import BaseAppConfig


class Stats(BaseModel):
    db: dict[str, int]  # collection name -> count
    logfile: int  # size in bytes
    system_log: int  # count


class SystemService:
    def __init__(self, app_config: BaseAppConfig, logger: Logger, db: BaseDb) -> None:
        self.logger = logger
        self.db = db
        self.logfile = app_config.data_dir / "app.log"

    def get_stats(self) -> Stats:
        db_stats = {}
        for col in self.db.database.list_collection_names():
            db_stats[col] = self.db.database[col].estimated_document_count()
        return Stats(db=db_stats, logfile=self.logfile.stat().st_size, system_log=self.db.dlog.count({}))

    def read_logfile(self) -> str:
        return self.logfile.read_text(encoding="utf-8")

    def clean_logfile(self) -> None:
        self.logfile.write_text("")
