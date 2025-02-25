import os
from abc import ABC, abstractmethod
from typing import cast

from bson import ObjectId
from mm_mongo import MongoConnection
from mm_std import Scheduler, init_logger

from mm_base3.base_db import BaseDb, DLog
from mm_base3.base_service import BaseServiceParams
from mm_base3.config import BaseAppConfig
from mm_base3.dconfig import DConfigDict, DConfigStorage
from mm_base3.dvalue import DValueDict, DValueStorage
from mm_base3.system_service import SystemService


class BaseCore[APP_CONFIG_T: BaseAppConfig, DCONFIG_T: DConfigDict, DVALUE_T: DValueDict, DB_T: BaseDb](ABC):
    def __init__(
        self,
        app_config_settings: type[APP_CONFIG_T],
        dconfig_settings: type[DCONFIG_T],
        dvalue_settings: type[DVALUE_T],
        db_settings: type[DB_T],
        debug_scheduler: bool = False,
    ) -> None:
        self.app_config = app_config_settings()
        self.logger = init_logger("app", file_path=f"{self.app_config.data_dir}/app.log", level=self.app_config.logger_level)
        conn = MongoConnection(self.app_config.database_url)
        self.mongo_client = conn.client
        self.database = conn.database
        self.db: DB_T = db_settings.init_collections(self.database)

        self.system_service: SystemService = SystemService(self.app_config, self.logger, self.db)

        self.dconfig: DCONFIG_T = cast(DCONFIG_T, DConfigStorage.init_storage(self.db.dconfig, dconfig_settings, self.dlog))
        self.dvalue: DVALUE_T = cast(DVALUE_T, DValueStorage.init_storage(self.db.dvalue, dvalue_settings))

        self.scheduler = Scheduler(self.logger, debug=debug_scheduler)

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
    def base_service_params(self) -> BaseServiceParams[APP_CONFIG_T, DCONFIG_T, DVALUE_T, DB_T]:
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
