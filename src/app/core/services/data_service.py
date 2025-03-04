import random

from bson import ObjectId
from mm_std import hr
from pymongo.results import InsertManyResult, InsertOneResult

from app.config import AppConfig, DConfigSettings, DValueSettings
from app.core.db import Data, DataStatus, Db
from mm_base3 import BaseService, BaseServiceParams


class DataService(BaseService[AppConfig, DConfigSettings, DValueSettings, Db]):
    def __init__(self, base_params: BaseServiceParams[AppConfig, DConfigSettings, DValueSettings, Db]) -> None:
        super().__init__(base_params)

    def generate_data(self) -> InsertOneResult:
        status = random.choice(list(DataStatus))
        value = random.randint(0, 1_000_000)
        self.logger.debug("generate_data %s %s", status, value)
        res = hr("https://httpbin.org/get")
        self.dlog("data_generated", {"status": status, "value": value, "res": res.json, "large-data": "abc" * 100})
        # print(type(self.dconfig))
        self.dlog("ddd", self.dconfig.telegram_token)

        # self.send_telegram_message(f"a new data: {value}")
        return self.db.data.insert_one(Data(id=ObjectId(), status=status, value=value))

    def generate_many(self) -> InsertManyResult:
        new_data_list = [
            Data(id=ObjectId(), status=random.choice(list(DataStatus)), value=random.randint(0, 1_000_000)) for _ in range(10)
        ]
        return self.db.data.insert_many(new_data_list)
