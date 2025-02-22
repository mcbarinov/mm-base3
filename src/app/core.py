from app.config import AppConfig
from app.db import Db
from app.services.data_service import DataService
from mm_base3 import BaseCore
from mm_base3.base_service import BaseServiceParams


class Core(BaseCore):
    def __init__(self, config: AppConfig) -> None:
        super().__init__(config)
        self.db = Db(self.database)
        base_params: BaseServiceParams[AppConfig, Db] = self.base_service_params(config, self.db)

        self.data_service = DataService(base_params)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
