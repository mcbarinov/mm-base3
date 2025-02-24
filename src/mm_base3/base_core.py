import os
from abc import ABC, abstractmethod
from typing import cast

from mm_mongo import MongoConnection
from mm_std import Scheduler, init_logger

from mm_base3.base_db import BaseDb
from mm_base3.base_service import BaseServiceParams
from mm_base3.config import BaseAppConfig
from mm_base3.services.dconfig_service import DConfigDict, DConfigService
from mm_base3.services.dlog_service import DLogService
from mm_base3.services.system_service import SystemService


class BaseCore[APP_CONFIG: BaseAppConfig, DCONFIG: DConfigDict, DB: BaseDb](ABC):
    def __init__(
        self,
        app_config_settings: type[APP_CONFIG],
        dconfig_settings: type[DCONFIG],
        db_settings: type[DB],
        debug_scheduler: bool = False,
    ) -> None:
        self.app_config = app_config_settings()
        self.logger = init_logger("app", file_path=f"{self.app_config.data_dir}/app.log", level=self.app_config.logger_level)
        conn = MongoConnection(self.app_config.database_url)
        self.mongo_client = conn.client
        self.database = conn.database
        self.db: DB = db_settings.init_collections(self.database)
        self.dlog_service: DLogService = DLogService(self.db, self.logger)
        self.dconfig_service = DConfigService(self.db, self.dlog_service)
        self.system_service: SystemService = SystemService(self.app_config, self.logger, self.db)

        self.dconfig: DCONFIG = cast(DCONFIG, self.dconfig_service.init_storage(dconfig_settings))

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
        self.dlog_service.dlog(category, data)

    @property
    def base_service_params(self) -> BaseServiceParams[APP_CONFIG, DCONFIG, DB]:
        return BaseServiceParams(
            logger=self.logger,
            app_config=self.app_config,
            dconfig=self.dconfig,
            db=self.db,
            dlog=self.dlog,
        )

    # def base_service_params(
    #     self, app_config: BaseAppConfig, dconfig: DCONFIG, db: BaseDb
    # ) -> BaseServiceParams[APP_CONFIG, DCONFIG, DB]:
    #     return BaseServiceParams[APP_CONFIG, DCONFIG, DB](
    #         logger=self.logger,
    #         app_config=app_config,
    #         dconfig=dconfig,
    #         db=db,
    #         system_log=self.system_log,
    #     )  # type: ignore[arg-type]

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


type BaseCoreAny = BaseCore[BaseAppConfig, DConfigDict, BaseDb]
