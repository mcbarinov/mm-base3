from app.core.db import Db
from app.core.services.data_service import DataService
from app.settings import DConfigSettings, DValueSettings
from mm_base3 import BaseCore, CoreConfig


class Core(BaseCore[DConfigSettings, DValueSettings, Db]):
    def __init__(self) -> None:
        super().__init__(CoreConfig(), DConfigSettings, DValueSettings, Db)

        self.data_service = DataService(self.base_service_params)

        self.scheduler.add_job(self.data_service.generate_data, 60, run_immediately=False)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
