import threading
from logging import Logger

import pydash
import toml
from mm_std import Scheduler
from pydantic import BaseModel

from mm_base3.config import BaseAppConfig
from mm_base3.core.base_db import BaseDb, DConfigType
from mm_base3.core.dconfig import DConfigStorage
from mm_base3.core.dvalue import DValueStorage
from mm_base3.errors import UserError


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


class DConfigInfo(BaseModel):
    dconfig: dict[str, object]
    descriptions: dict[str, str]
    types: dict[str, DConfigType]
    hidden: set[str]


class DValueInfo(BaseModel):
    dvalue: dict[str, object]
    persistent: dict[str, bool]
    descriptions: dict[str, str]


# noinspection PyMethodMayBeStatic
class SystemService:
    def __init__(self, app_config: BaseAppConfig, logger: Logger, db: BaseDb, scheduler: Scheduler) -> None:
        self.logger = logger
        self.db = db
        self.logfile = app_config.data_dir / "app.log"
        self.scheduler = scheduler

    # dconfig

    def get_dconfig_info(self) -> DConfigInfo:
        return DConfigInfo(
            dconfig=DConfigStorage.storage,
            descriptions=DConfigStorage.descriptions,
            types=DConfigStorage.types,
            hidden=DConfigStorage.hidden,
        )

    def export_dconfig_as_toml(self) -> str:
        result = pydash.omit(DConfigStorage.storage, *DConfigStorage.hidden)
        return toml.dumps(result)

    def update_dconfig_from_toml(self, toml_value: str) -> bool | None:
        data = toml.loads(toml_value)
        if isinstance(data, dict):
            return DConfigStorage.update({key: str(value) for key, value in data.items()})

    def update_dconfig(self, data: dict[str, str]) -> bool:
        return DConfigStorage.update(data)

    # dvalue
    def get_dvalue_info(self) -> DValueInfo:
        return DValueInfo(
            dvalue=DValueStorage.storage,
            persistent=DValueStorage.persistent,
            descriptions=DValueStorage.descriptions,
        )

    def export_dvalue_as_toml(self) -> str:
        return toml.dumps(DValueStorage.storage)

    def export_dvalue_field_as_toml(self, key: str) -> str:
        return toml.dumps({key: DValueStorage.storage[key]})

    def get_dvalue_value(self, key: str) -> object:
        return DValueStorage.storage[key]

    def update_dvalue_field(self, key: str, toml_str: str) -> None:
        data = toml.loads(toml_str)
        if key not in data:
            raise UserError(f"Key '{key}' not found in toml data")
        DValueStorage.storage[key] = data[key]

    # system

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
