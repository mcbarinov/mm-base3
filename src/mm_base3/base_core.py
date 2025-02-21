import os
from abc import ABC, abstractmethod

from mm_mongo import MongoConnection
from mm_std import Scheduler, init_logger

from mm_base3.config import BaseConfig
from mm_base3.system_service import SystemService


class BaseCore(ABC):
    def __init__(self, config: BaseConfig, debug_scheduler: bool = False) -> None:
        self.config = config
        self.logger = init_logger("app", file_path=f"{config.data_dir}/app.log", level=config.logger_level)
        conn = MongoConnection(config.database_url)
        self.mongo_client = conn.client
        self.database = conn.database
        self.system_service = SystemService(self.logger, self.database)
        self.scheduler = Scheduler(self.logger, debug=debug_scheduler)

    def startup(self) -> None:
        self.logger.debug("app started")
        self.scheduler.start()
        self.start()
        if not self.config.debug:
            self.system_service.system_log("app_start")

    def shutdown(self) -> None:
        self.scheduler.stop()
        if not self.config.debug:
            self.system_service.system_log("app_stop")
        self.stop()
        self.mongo_client.close()
        self.logger.debug("app stopped")
        # noinspection PyUnresolvedReferences
        os._exit(0)

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
