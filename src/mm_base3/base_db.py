from datetime import datetime
from enum import Enum, unique
from typing import Any, ClassVar, Self, get_args

from bson import ObjectId
from mm_mongo import DatabaseAny, MongoCollection, MongoModel
from mm_std import utc_now
from pydantic import BaseModel, ConfigDict, Field


@unique
class DConfigType(str, Enum):
    STRING = "STRING"
    MULTILINE = "MULTILINE"
    DATETIME = "DATETIME"
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    DECIMAL = "DECIMAL"


class DConfig(MongoModel[str]):
    type: DConfigType
    value: str
    updated_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)

    __collection__: str = "dconfig"
    __validator__: ClassVar[dict[str, object]] = {
        "$jsonSchema": {
            "required": ["type", "value", "updated_at", "created_at"],
            "additionalProperties": False,
            "properties": {
                "_id": {"bsonType": "string"},
                "type": {"enum": ["STRING", "MULTILINE", "DATETIME", "BOOLEAN", "INTEGER", "FLOAT", "DECIMAL"]},
                "value": {"bsonType": "string"},
                "updated_at": {"bsonType": ["date", "null"]},
                "created_at": {"bsonType": "date"},
            },
        },
    }


class DLog(MongoModel[ObjectId]):
    category: str
    data: object
    created_at: datetime = Field(default_factory=utc_now)

    __collection__: str = "dlog"
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


class DValue(MongoModel[str]):
    value: str
    updated_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)

    __collection__: str = "dvalue"
    __validator__: ClassVar[dict[str, object]] = {
        "$jsonSchema": {
            "required": ["value", "updated_at", "created_at"],
            "additionalProperties": False,
            "properties": {
                "_id": {"bsonType": "string"},
                "value": {"bsonType": "string"},
                "updated_at": {"bsonType": ["date", "null"]},
                "created_at": {"bsonType": "date"},
            },
        },
    }


class BaseDb(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    dlog: MongoCollection[ObjectId, DLog]
    dconfig: MongoCollection[str, DConfig]
    dvalue: MongoCollection[str, DValue]

    database: DatabaseAny

    @classmethod
    def init_collections(cls, database: DatabaseAny) -> Self:
        # Collect all class-level attributes, including those from base classes
        attributes = {}
        for base in cls.__mro__:
            if hasattr(base, "__annotations__"):
                attributes.update(base.__annotations__)

        data: dict[str, MongoCollection[Any, Any]] = {}
        for key, value in attributes.items():
            if key == "database":
                continue
            model = get_args(value)[1]
            data[key] = MongoCollection(database, model)
        return cls(**data, database=database)
