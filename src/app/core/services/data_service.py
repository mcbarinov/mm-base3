import random

from bson import ObjectId
from mm_std import hr
from pymongo.results import InsertManyResult, InsertOneResult

from app.core.db import Data, DataStatus, Db
from app.settings import DConfigSettings, DValueSettings
from mm_base3 import BaseService, BaseServiceParams


class DataService(BaseService[DConfigSettings, DValueSettings, Db]):
    def __init__(self, base_params: BaseServiceParams[DConfigSettings, DValueSettings, Db]) -> None:
        super().__init__(base_params)

    def generate_data(self) -> InsertOneResult:
        status = random.choice(list(DataStatus))
        value = random.randint(0, 1_000_000)

        return self.db.data.insert_one(Data(id=ObjectId(), status=status, value=value))

    def generate_many(self) -> InsertManyResult:
        res = hr("https://httpbin.org/get")
        self.dlog("generate_many", {"res": res.json, "large-data": "abc" * 100})
        self.dlog("ddd", self.dconfig.telegram_token)
        new_data_list = [
            Data(id=ObjectId(), status=random.choice(list(DataStatus)), value=random.randint(0, 1_000_000)) for _ in range(10)
        ]
        return self.db.data.insert_many(new_data_list)
