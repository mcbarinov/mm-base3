from app.config import AppConfig, DConfigSettings, DValueSettings
from app.core.db import Db
from app.core.services.data_service import DataService
from mm_base3 import BaseCore


class Core(BaseCore[AppConfig, DConfigSettings, DValueSettings, Db]):
    def __init__(self) -> None:
        super().__init__(AppConfig(), DConfigSettings, DValueSettings(), Db)

        self.data_service = DataService(self.base_service_params)

        self.scheduler.add_job(self.data_service.generate_data, 60, run_immediately=False)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
