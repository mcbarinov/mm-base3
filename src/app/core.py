from app.db import Db
from app.services.data_service import DataService
from mm_base3 import BaseConfig, BaseCore


class Core(BaseCore):
    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self.db = Db(self.database)
        self.data_service = DataService(self.db)
