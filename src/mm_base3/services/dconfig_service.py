from __future__ import annotations

import itertools
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, ClassVar, cast, overload

import pydash
import toml
from mm_std import Err, Ok, Result, utc_now

from mm_base3.base_db import BaseDb, DConfig, DConfigType
from mm_base3.errors import UnregisteredSystemConfigError
from mm_base3.services.dlog_service import DLogService


class DC[T: (str, bool, int, float, Decimal)]:
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
        return cast(T, getattr(DConfigService.storage, self.key))

    def __set_name__(self, owner: object, name: str) -> None:
        self.key = name

    @staticmethod
    def get_attrs_from_settings(dconfig_settings: DConfigDict) -> list[DC[T]]:
        attrs: list[DC[T]] = []
        keys = get_registered_attributes(dconfig_settings)
        for key in keys:
            field = getattr(dconfig_settings.__class__, key)
            if isinstance(field, DC):
                attrs.append(field)
        attrs.sort(key=lambda x: x.order)

        return attrs


class DConfigDict(dict[str, object]):
    descriptions: ClassVar[dict[str, str]] = {}
    types: ClassVar[dict[str, DConfigType]] = {}
    hidden: ClassVar[set[str]] = set()

    def __getattr__(self, item: str) -> object:
        if item not in self:
            raise UnregisteredSystemConfigError(item)

        return self.get(item, None)

    def get_or_none(self, key: str) -> object | None:
        try:
            return self.get(key)
        except UnregisteredSystemConfigError:
            return None

    def get_non_hidden_keys(self) -> set[str]:
        return self.keys() - self.hidden

    def get_type(self, key: str) -> DConfigType:
        return self.types[key]

    @classmethod
    def get_attrs(cls) -> list[DC[Any]]:
        attrs: list[DC[Any]] = []
        keys = get_registered_attributes(cls)
        for key in keys:
            field = getattr(cls, key)
            if isinstance(field, DC):
                attrs.append(field)
        attrs.sort(key=lambda x: x.order)

        return attrs


@dataclass
class DConfigInitValue:
    key: str
    order: int
    description: str
    value: str | int | float | bool


class DConfigService:
    storage = DConfigDict()

    def __init__(self, db: BaseDb, dlog_service: DLogService) -> None:
        self.db = db
        self.dlog_service = dlog_service

    def init_storage(self, dconfig_settings: type[DConfigDict]) -> DConfigDict:
        for attr in dconfig_settings.get_attrs():
            type_ = get_type(attr.value)
            self.storage.descriptions[attr.key] = attr.description
            self.storage.types[attr.key] = type_
            if attr.hide:
                self.storage.hidden.add(attr.key)

            dv = self.db.dconfig.get_or_none(attr.key)
            if dv:
                typed_value_res = get_typed_value(dv.type, dv.value)
                if isinstance(typed_value_res, Ok):
                    self.storage[attr.key] = typed_value_res.ok
                else:
                    self.dlog_service.dlog("dconfig.get_typed_value", {"error": typed_value_res.err, "attr": attr.key})
            else:  # create rows if not exists
                self.db.dconfig.insert_one(DConfig(id=attr.key, type=type_, value=get_str_value(type_, attr.value)))
                self.storage[attr.key] = attr.value

        # remove rows which not in settings.DCONFIG
        self.db.dconfig.delete_many({"_id": {"$nin": get_registered_attributes(dconfig_settings)}})
        return self.storage

    def update_multiline(self, key: str, value: str) -> None:
        value = value.replace("\r", "")
        self.db.dconfig.set(key, {"value": value, "updated_at": utc_now()})
        self.storage[key] = value

    def update_dconfig_values(self, data: dict[str, str]) -> bool:
        result = True
        for key in data:
            if key in self.storage:
                str_value = data.get(key) or ""  # for BOOLEAN type (checkbox)
                str_value = str_value.replace("\r", "")  # for MULTILINE (textarea do it)
                type_value_res = get_typed_value(self.storage.types[key], str_value.strip())
                if isinstance(type_value_res, Ok):
                    self.db.dconfig.set(key, {"value": str_value, "updated_at": utc_now()})
                    self.storage[key] = type_value_res.ok
                else:
                    self.dlog_service.dlog("dconfig_service.update", {"error": type_value_res.err, "key": key})
                    result = False
            else:
                self.dlog_service.dlog("dconfig_service.update", {"error": "unknown key", "key": key})
                result = False
        return result

    def export_dconfig_as_toml(self) -> str:
        result = pydash.omit(self.storage, *self.storage.hidden)
        return toml.dumps(result)

    def update_dconfig_from_toml(self, toml_value: str) -> bool | None:
        data = toml.loads(toml_value)

        if isinstance(data, dict):
            return self.update_dconfig_values({key: str(value) for key, value in data.items()})

    # def update_dconfig_yaml(self, yaml_value: str) -> bool | None:
    #     data = yaml.full_load(yaml_value)
    #     if isinstance(data, dict):
    #         return self.update(data)
    #
    # def export_dconfig_yaml(self) -> str:
    #     result = pydash.omit(self.storage, *self.storage.hidden)
    #     return yaml.dump(result, explicit_end=True, default_style="'", sort_keys=False)
    #


def get_registered_attributes(obj: object) -> list[str]:
    return [x for x in dir(obj) if not x.startswith("_")]


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
