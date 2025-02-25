from app.config import AppConfig, DConfigSettings, DValueSettings
from app.db import Db
from app.services.data_service import DataService
from mm_base3 import BaseCore


class Core(BaseCore[AppConfig, DConfigSettings, DValueSettings, Db]):
    def __init__(self) -> None:
        super().__init__(AppConfig, DConfigSettings, DValueSettings, Db)

        self.data_service = DataService(self.base_service_params)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
