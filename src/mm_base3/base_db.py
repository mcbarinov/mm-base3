from datetime import datetime
from typing import ClassVar

from bson import ObjectId
from mm_mongo import DatabaseAny, MongoCollection, MongoModel
from mm_std import utc_now
from pydantic import Field


class SystemLog(MongoModel[ObjectId]):
    category: str
    data: object
    created_at: datetime = Field(default_factory=utc_now)

    __collection__: str = "system_log"
    __indexes__ = "category, created_at"
    __validator__: ClassVar[dict[str, object]] = {
        "$jsonSchema": {
            "required": ["category", "data", "created_at"],
            "additionalProperties": False,
            "properties": {
                "_id": {"bsonType": "objectId"},
                "category": {"bsonType": "string"},
                "data": {},
                "created_at": {"bsonType": "date"},
            },
        },
    }


class BaseDb:
    system_log: MongoCollection[ObjectId, SystemLog]

    def __init__(self, database: DatabaseAny) -> None:
        self.system_log = MongoCollection(database, SystemLog)
