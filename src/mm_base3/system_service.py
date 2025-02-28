import threading
from logging import Logger

import pydash
from mm_std import Scheduler
from pydantic import BaseModel

from mm_base3.base_db import BaseDb
from mm_base3.config import BaseAppConfig


class Stats(BaseModel):
    class ThreadInfo(BaseModel):
        name: str
        daemon: bool
        func_name: str | None

    db: dict[str, int]  # collection name -> count
    logfile: int  # size in bytes
    system_log: int  # count
    threads: list[ThreadInfo]
    scheduler_jobs: list[Scheduler.Job]


class SystemService:
    def __init__(self, app_config: BaseAppConfig, logger: Logger, db: BaseDb, scheduler: Scheduler) -> None:
        self.logger = logger
        self.db = db
        self.logfile = app_config.data_dir / "app.log"
        self.scheduler = scheduler

    def get_stats(self) -> Stats:
        # threads
        threads = []
        for t in threading.enumerate():
            target = t.__dict__.get("_target")
            func_name = None
            if target:
                func_name = target.__qualname__
            threads.append(Stats.ThreadInfo(name=t.name, daemon=t.daemon, func_name=func_name))
        threads = pydash.sort(threads, key=lambda x: x.name)

        # db
        db_stats = {}
        for col in self.db.database.list_collection_names():
            db_stats[col] = self.db.database[col].estimated_document_count()

        return Stats(
            db=db_stats,
            logfile=self.logfile.stat().st_size,
            system_log=self.db.dlog.count({}),
            threads=threads,
            scheduler_jobs=self.scheduler.jobs,
        )

    def read_logfile(self) -> str:
        return self.logfile.read_text(encoding="utf-8")

    def clean_logfile(self) -> None:
        self.logfile.write_text("")
