from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from logging import Logger
from typing import Generic, TypeVar, cast

from bson import ObjectId
from mm_mongo import MongoConnection
from mm_std import Scheduler, init_logger

from mm_base3.config import BaseAppConfig
from mm_base3.core.base_db import BaseDb, DLog
from mm_base3.core.dconfig import DConfigDict, DConfigStorage
from mm_base3.core.dvalue import DValueDict, DValueStorage
from mm_base3.core.system_service import SystemService

APP_CONFIG_co = TypeVar("APP_CONFIG_co", bound=BaseAppConfig, covariant=True)
DCONFIG_co = TypeVar("DCONFIG_co", bound=DConfigDict, covariant=True)
DVALUE_co = TypeVar("DVALUE_co", bound=DValueDict, covariant=True)
DB_co = TypeVar("DB_co", bound=BaseDb, covariant=True)


APP_CONFIG = TypeVar("APP_CONFIG", bound=BaseAppConfig)
DCONFIG = TypeVar("DCONFIG", bound=DConfigDict)
DVALUE = TypeVar("DVALUE", bound=DValueDict)
DB = TypeVar("DB", bound=BaseDb)


class BaseCore(Generic[APP_CONFIG_co, DCONFIG_co, DVALUE_co, DB_co], ABC):
    def __init__(
        self,
        app_config_settings: APP_CONFIG_co,
        dconfig_settings: DCONFIG_co,
        dvalue_settings: DVALUE_co,
        db_settings: type[DB_co],
        debug_scheduler: bool = False,
    ) -> None:
        print("000", type(dconfig_settings))
        self.app_config = app_config_settings
        self.logger = init_logger("app", file_path=f"{self.app_config.data_dir}/app.log", level=self.app_config.logger_level)
        self.scheduler = Scheduler(self.logger, debug=debug_scheduler)
        conn = MongoConnection(self.app_config.database_url)
        self.mongo_client = conn.client
        self.database = conn.database
        self.db: DB_co = db_settings.init_collections(self.database)

        self.system_service: SystemService = SystemService(self.app_config, self.logger, self.db, self.scheduler)

        self.dconfig = DConfigStorage.init_storage(self.db.dconfig, dconfig_settings, self.dlog)
        print("111", type(self.dconfig))

        # print(self.dconfig.non_existing_field)

        self.dvalue: DVALUE_co = cast(DVALUE_co, DValueStorage.init_storage(self.db.dvalue, dvalue_settings))

    def startup(self) -> None:
        self.scheduler.start()
        self.start()
        self.logger.debug("app started")
        if not self.app_config.debug:
            self.dlog("app_start")

    def shutdown(self) -> None:
        self.scheduler.stop()
        if not self.app_config.debug:
            self.dlog("app_stop")
        self.stop()
        self.mongo_client.close()
        self.logger.debug("app stopped")
        # noinspection PyUnresolvedReferences
        os._exit(0)

    def dlog(self, category: str, data: object = None) -> None:
        self.logger.debug("system_log %s %s", category, data)
        self.db.dlog.insert_one(DLog(id=ObjectId(), category=category, data=data))

    @property
    def base_service_params(self) -> BaseServiceParams[APP_CONFIG_co, DCONFIG_co, DVALUE_co, DB_co]:
        return BaseServiceParams(
            logger=self.logger,
            app_config=self.app_config,
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


type BaseCoreAny = BaseCore[BaseAppConfig, DConfigDict, DValueDict, BaseDb]


@dataclass
class BaseServiceParams(Generic[APP_CONFIG, DCONFIG, DVALUE, DB]):
    app_config: APP_CONFIG
    dconfig: DCONFIG
    dvalue: DVALUE
    db: DB
    logger: Logger
    dlog: Callable[[str, object], None]


class BaseService(Generic[APP_CONFIG_co, DCONFIG_co, DVALUE_co, DB_co]):
    def __init__(self, base_params: BaseServiceParams[APP_CONFIG_co, DCONFIG_co, DVALUE_co, DB_co]) -> None:
        self.app_config = base_params.app_config
        self.dconfig: DCONFIG_co = base_params.dconfig
        self.dvalue: DVALUE_co = base_params.dvalue
        self.db = base_params.db
        self.logger = base_params.logger
        self.dlog = base_params.dlog
