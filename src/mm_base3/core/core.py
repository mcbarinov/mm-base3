from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from logging import Logger
from typing import Generic, TypeVar

from bson import ObjectId
from mm_mongo import MongoConnection
from mm_std import Scheduler, init_logger

from mm_base3.core.config import CoreConfig
from mm_base3.core.db import BaseDb, DLog
from mm_base3.core.dconfig import DConfigModel, DConfigStorage
from mm_base3.core.dvalue import DValueModel, DValueStorage
from mm_base3.core.system_service import SystemService

DCONFIG_co = TypeVar("DCONFIG_co", bound=DConfigModel, covariant=True)
DVALUE_co = TypeVar("DVALUE_co", bound=DValueModel, covariant=True)
DB_co = TypeVar("DB_co", bound=BaseDb, covariant=True)


DCONFIG = TypeVar("DCONFIG", bound=DConfigModel)
DVALUE = TypeVar("DVALUE", bound=DValueModel)
DB = TypeVar("DB", bound=BaseDb)


class BaseCore(Generic[DCONFIG_co, DVALUE_co, DB_co], ABC):
    def __init__(
        self,
        core_config: CoreConfig,
        dconfig_settings: type[DCONFIG_co],
        dvalue_settings: type[DVALUE_co],
        db_settings: type[DB_co],
        debug_scheduler: bool = False,
    ) -> None:
        self.core_config = core_config
        self.logger = init_logger("app", file_path=f"{core_config.data_dir}/app.log", level=core_config.logger_level)
        self.scheduler = Scheduler(self.logger, debug=debug_scheduler)
        conn = MongoConnection(self.core_config.database_url)
        self.mongo_client = conn.client
        self.database = conn.database
        self.db: DB_co = db_settings.init_collections(self.database)

        self.system_service: SystemService = SystemService(self.core_config, self.logger, self.db, self.scheduler)

        self.dconfig: DCONFIG_co = DConfigStorage.init_storage(self.db.dconfig, dconfig_settings, self.dlog)
        self.dvalue: DVALUE_co = DValueStorage.init_storage(self.db.dvalue, dvalue_settings)

    def startup(self) -> None:
        self.scheduler.start()
        self.start()
        self.logger.debug("app started")
        if not self.core_config.debug:
            self.dlog("app_start")

    def shutdown(self) -> None:
        self.scheduler.stop()
        if not self.core_config.debug:
            self.dlog("app_stop")
        self.stop()
        self.mongo_client.close()
        self.logger.debug("app stopped")
        # noinspection PyUnresolvedReferences,PyProtectedMember
        os._exit(0)

    def dlog(self, category: str, data: object = None) -> None:
        self.logger.debug("system_log %s %s", category, data)
        self.db.dlog.insert_one(DLog(id=ObjectId(), category=category, data=data))

    @property
    def base_service_params(self) -> BaseServiceParams[DCONFIG_co, DVALUE_co, DB_co]:
        return BaseServiceParams(
            logger=self.logger,
            core_config=self.core_config,
            dconfig=self.dconfig,
            dvalue=self.dvalue,
            db=self.db,
            dlog=self.dlog,
        )

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


type BaseCoreAny = BaseCore[DConfigModel, DValueModel, BaseDb]


@dataclass
class BaseServiceParams(Generic[DCONFIG, DVALUE, DB]):
    core_config: CoreConfig
    dconfig: DCONFIG
    dvalue: DVALUE
    db: DB
    logger: Logger
    dlog: Callable[[str, object], None]


class BaseService(Generic[DCONFIG_co, DVALUE_co, DB_co]):
    def __init__(self, base_params: BaseServiceParams[DCONFIG_co, DVALUE_co, DB_co]) -> None:
        self.core_config = base_params.core_config
        self.dconfig: DCONFIG_co = base_params.dconfig
        self.dvalue: DVALUE_co = base_params.dvalue
        self.db = base_params.db
        self.logger = base_params.logger
        self.dlog = base_params.dlog
