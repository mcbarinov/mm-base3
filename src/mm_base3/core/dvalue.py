from __future__ import annotations

import base64
import itertools
import pickle  # nosec: B403
from typing import Any, ClassVar, cast, overload

import toml
from mm_mongo import MongoCollection
from mm_std import synchronized, utc_now

from mm_base3.core.base_db import DValue
from mm_base3.core.utils import get_registered_public_attributes
from mm_base3.errors import UnregisteredDValueError


class DV[T]:
    _counter = itertools.count()

    def __init__(self, value: T, description: str = "", persistent: bool = True) -> None:
        self.value = value
        self.description = description
        self.persistent = persistent
        self.order = next(DV._counter)

    @overload
    def __get__(self, obj: None, obj_type: None) -> DV[T]: ...

    @overload
    def __get__(self, obj: object, obj_type: type) -> T: ...

    def __get__(self, obj: object | None, obj_type: type | None = None) -> T | DV[T]:
        if obj is None:
            return self
        return cast(T, getattr(DValueStorage.storage, self.key))

    def __set__(self, instance: object, value: T) -> None:
        setattr(DValueStorage.storage, self.key, value)

    def __set_name__(self, owner: object, name: str) -> None:
        self.key = name


class DValueModel:
    pass


class DValueDict(dict[str, object]):
    persistent: ClassVar[dict[str, bool]] = {}
    descriptions: ClassVar[dict[str, str]] = {}

    def __getattr__(self, item: str) -> object:
        if item not in self:
            raise UnregisteredDValueError(item)
        return self.get(item)

    def __setattr__(self, key: str, value: object) -> None:
        if key not in self:
            raise UnregisteredDValueError(key)
        if DValueDict.persistent[key]:
            DValueStorage.update_persistent_value(key, value)
        self[key] = value

    def init_value(self, key: str, value: object, description: str, persistent: bool) -> None:
        DValueDict.persistent[key] = persistent
        DValueDict.descriptions[key] = description
        self[key] = value
        if persistent:
            DValueStorage.init_persistent_value(key, value)


class DValueStorage:
    storage = DValueDict()
    collection: MongoCollection[str, DValue]

    @classmethod
    @synchronized
    def init_storage[DVALUE: DValueModel](cls, collection: MongoCollection[str, DValue], dvalue_settings: type[DVALUE]) -> DVALUE:
        cls.collection = collection
        persistent_keys = []

        for attr in get_attrs(dvalue_settings):
            value = attr.value
            # get value from db if exists
            if attr.persistent:
                persistent_keys.append(attr.key)
                dvalue_from_db = collection.get_or_none(attr.key)
                if dvalue_from_db:
                    value = decode_value(dvalue_from_db.value)
            cls.storage.init_value(attr.key, value, attr.description, attr.persistent)

        # remove rows which not in persistent_keys
        collection.delete_many({"_id": {"$nin": persistent_keys}})
        return cast(DVALUE, cls.storage)

    @classmethod
    def init_persistent_value(cls, key: str, value: object) -> None:
        if not cls.collection.exists({"_id": key}):
            cls.collection.insert_one(DValue(id=key, value=encode_value(value)))
        else:
            cls.update_persistent_value(key, value)

    @classmethod
    def update_persistent_value(cls, key: str, value: object) -> None:
        cls.collection.update(key, {"$set": {"value": encode_value(value), "updated_at": utc_now()}})

    @classmethod
    def export_as_toml(cls) -> str:
        return toml.dumps(cls.storage)

    @classmethod
    def export_field_as_toml(cls, key: str) -> str:
        return toml.dumps({key: cls.storage[key]})

    @classmethod
    def get_value(cls, key: str) -> object:
        return cls.storage[key]


def encode_value(value: object) -> str:
    return base64.b64encode(pickle.dumps(value)).decode("utf-8")


def decode_value(value: str) -> object:
    return pickle.loads(base64.b64decode(value))  # noqa: S301 # nosec


# noinspection DuplicatedCode
def get_attrs(dconfig_settings: type[DValueModel]) -> list[DV[Any]]:
    attrs: list[DV[Any]] = []
    keys = get_registered_public_attributes(dconfig_settings)
    for key in keys:
        field = getattr(dconfig_settings, key)
        if isinstance(field, DV):
            attrs.append(field)
    attrs.sort(key=lambda x: x.order)
    return attrs
