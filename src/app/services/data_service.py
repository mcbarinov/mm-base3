import random

from bson import ObjectId
from pymongo.results import InsertManyResult, InsertOneResult

from app.db import Data, DataStatus, Db


class DataService:
    def __init__(self, db: Db) -> None:
        self.db = db

    def generate_data(self) -> InsertOneResult:
        status = random.choice(list(DataStatus))
        value = random.randint(0, 1_000_000)
        # self.dlog("data_generated", {"status": status, "value": value, "large-data": "abc" * 100})
        # self.send_telegram_message(f"a new data: {value}")

        return self.db.data.insert_one(Data(id=ObjectId(), status=status, value=value))

    def generate_many(self) -> InsertManyResult:
        new_data_list = [
            Data(id=ObjectId(), status=random.choice(list(DataStatus)), value=random.randint(0, 1_000_000)) for _ in range(10)
        ]
        return self.db.data.insert_many(new_data_list)
