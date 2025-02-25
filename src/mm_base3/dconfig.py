from __future__ import annotations

import itertools
from collections.abc import Callable
from decimal import Decimal
from typing import Any, ClassVar, cast, overload

import pydash
import toml
from mm_mongo import MongoCollection
from mm_std import Err, Ok, Result, synchronized, utc_now

from mm_base3.base_db import DConfig, DConfigType
from mm_base3.errors import UnregisteredDConfigError
from mm_base3.utils import get_registered_public_attributes


class DC[T: (str, bool, int, float, Decimal)]:
    """DC stands for Dynamic Config. It is used to define a dynamic config attribute in a dconfig_settings class."""

    _counter = itertools.count()

    def __init__(self, value: T, description: str = "", hide: bool = False) -> None:
        self.value: T = value
        self.description = description
        self.hide = hide
        self.order = next(DC._counter)

    @overload
    def __get__(self, obj: None, obj_type: None) -> DC[T]: ...

    @overload
    def __get__(self, obj: object, obj_type: type) -> T: ...

    def __get__(self, obj: object, obj_type: type | None = None) -> T | DC[T]:
        if obj is None:
            return self
        return cast(T, getattr(DConfigStorage.storage, self.key))

    def __set_name__(self, owner: object, name: str) -> None:
        self.key = name


class DConfigDict(dict[str, object]):
    descriptions: ClassVar[dict[str, str]] = {}
    types: ClassVar[dict[str, DConfigType]] = {}
    hidden: ClassVar[set[str]] = set()

    def __getattr__(self, item: str) -> object:
        if item not in self:
            raise UnregisteredDConfigError(item)

        return self.get(item, None)

    def get_or_none(self, key: str) -> object | None:
        try:
            return self.get(key)
        except UnregisteredDConfigError:
            return None

    def get_non_hidden_keys(self) -> set[str]:
        return self.keys() - self.hidden

    def get_type(self, key: str) -> DConfigType:
        return self.types[key]

    @classmethod
    def get_attrs(cls) -> list[DC[Any]]:
        attrs: list[DC[Any]] = []
        keys = get_registered_public_attributes(cls)
        for key in keys:
            field = getattr(cls, key)
            if isinstance(field, DC):
                attrs.append(field)
        attrs.sort(key=lambda x: x.order)

        return attrs


class DConfigStorage:
    storage = DConfigDict()
    collection: MongoCollection[str, DConfig]
    dlog: Callable[[str, object], None]

    @classmethod
    @synchronized
    def init_storage(
        cls, collection: MongoCollection[str, DConfig], dconfig_settings: type[DConfigDict], dlog: Callable[[str, object], None]
    ) -> DConfigDict:
        cls.collection = collection
        cls.dlog = dlog

        for attr in dconfig_settings.get_attrs():
            type_ = get_type(attr.value)
            cls.storage.descriptions[attr.key] = attr.description
            cls.storage.types[attr.key] = type_
            if attr.hide:
                cls.storage.hidden.add(attr.key)

            dv = collection.get_or_none(attr.key)
            if dv:
                typed_value_res = get_typed_value(dv.type, dv.value)
                if isinstance(typed_value_res, Ok):
                    cls.storage[attr.key] = typed_value_res.ok
                else:
                    dlog("dconfig.get_typed_value", {"error": typed_value_res.err, "attr": attr.key})
            else:  # create rows if not exists
                collection.insert_one(DConfig(id=attr.key, type=type_, value=get_str_value(type_, attr.value)))
                cls.storage[attr.key] = attr.value

        # remove rows which not in settings.DCONFIG
        collection.delete_many({"_id": {"$nin": get_registered_public_attributes(dconfig_settings)}})
        return cls.storage

    @classmethod
    def update_multiline(cls, key: str, value: str) -> None:
        value = value.replace("\r", "")
        cls.collection.set(key, {"value": value, "updated_at": utc_now()})
        cls.storage[key] = value

    @classmethod
    def update(cls, data: dict[str, str]) -> bool:
        result = True
        for key in data:
            if key in cls.storage:
                str_value = data.get(key) or ""  # for BOOLEAN type (checkbox)
                str_value = str_value.replace("\r", "")  # for MULTILINE (textarea do it)
                type_value_res = get_typed_value(cls.storage.types[key], str_value.strip())
                if isinstance(type_value_res, Ok):
                    cls.collection.set(key, {"value": str_value, "updated_at": utc_now()})
                    cls.storage[key] = type_value_res.ok
                else:
                    cls.dlog("DConfigStorage.update", {"error": type_value_res.err, "key": key})
                    result = False
            else:
                cls.dlog("DConfigStorage.update", {"error": "unknown key", "key": key})
                result = False
        return result

    @classmethod
    def export_as_toml(cls) -> str:
        result = pydash.omit(cls.storage, *cls.storage.hidden)
        return toml.dumps(result)

    @classmethod
    def update_from_toml(cls, toml_value: str) -> bool | None:
        data = toml.loads(toml_value)

        if isinstance(data, dict):
            return cls.update({key: str(value) for key, value in data.items()})


def get_type(value: object) -> DConfigType:
    if isinstance(value, bool):
        return DConfigType.BOOLEAN
    if isinstance(value, str):
        return DConfigType.MULTILINE if "\n" in value else DConfigType.STRING
    if isinstance(value, Decimal):
        return DConfigType.DECIMAL
    if isinstance(value, int):
        return DConfigType.INTEGER
    if isinstance(value, float):
        return DConfigType.FLOAT
    raise ValueError(f"unsupported type: {type(value)}")


def get_typed_value(type_: DConfigType, str_value: str) -> Result[Any]:
    try:
        if type_ == DConfigType.BOOLEAN:
            return Ok(str_value.lower() == "true")
        if type_ == DConfigType.INTEGER:
            return Ok(int(str_value))
        if type_ == DConfigType.FLOAT:
            return Ok(float(str_value))
        if type_ == DConfigType.DECIMAL:
            return Ok(Decimal(str_value))
        if type_ == DConfigType.STRING:
            return Ok(str_value)
        if type_ == DConfigType.MULTILINE:
            return Ok(str_value.replace("\r", ""))
        return Err(f"unsupported type: {type_}")
    except Exception as e:
        return Err(str(e))


def get_str_value(type_: DConfigType, value: object) -> str:
    if type_ is DConfigType.BOOLEAN:
        return "True" if value else ""
    return str(value)
