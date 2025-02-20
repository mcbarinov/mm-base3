from datetime import datetime
from enum import Enum, unique
from typing import ClassVar

from bson import ObjectId
from mm_mongo import DatabaseAny, MongoCollection, MongoModel
from mm_std import utc_now
from pydantic import Field


@unique
class DataStatus(str, Enum):
    OK = "OK"
    ERROR = "ERROR"


class Data(MongoModel[ObjectId]):
    status: DataStatus
    value: int
    created_at: datetime = Field(default_factory=utc_now)

    __collection__: str = "data"
    __indexes__ = "status, created_at"
    __validator__: ClassVar[dict[str, object]] = {
        "$jsonSchema": {
            "required": ["status", "value", "created_at"],
            "additionalProperties": False,
            "properties": {
                "_id": {"bsonType": "objectId"},
                "status": {"enum": ["OK", "ERROR"]},
                "value": {"bsonType": "int"},
                "created_at": {"bsonType": "date"},
            },
        },
    }


class Db:
    data: MongoCollection[ObjectId, Data]

    def __init__(self, database: DatabaseAny) -> None:
        self.data = MongoCollection(database, Data)
