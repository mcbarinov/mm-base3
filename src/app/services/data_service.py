import random

from bson import ObjectId
from pymongo.results import InsertManyResult, InsertOneResult

from app.config import AppConfig
from app.db import Data, DataStatus, Db
from mm_base3 import BaseService
from mm_base3.base_service import BaseServiceParams


class DataService(BaseService[AppConfig, Db]):
    def __init__(self, base_params: BaseServiceParams[AppConfig, Db]) -> None:
        super().__init__(base_params)

    def generate_data(self) -> InsertOneResult:
        status = random.choice(list(DataStatus))
        value = random.randint(0, 1_000_000)
        self.logger.debug("generate_data %s %s", status, value)

        # self.dlog("data_generated", {"status": status, "value": value, "large-data": "abc" * 100})
        # self.send_telegram_message(f"a new data: {value}")

        return self.db.data.insert_one(Data(id=ObjectId(), status=status, value=value))

    def generate_many(self) -> InsertManyResult:
        new_data_list = [
            Data(id=ObjectId(), status=random.choice(list(DataStatus)), value=random.randint(0, 1_000_000)) for _ in range(10)
        ]
        return self.db.data.insert_many(new_data_list)
