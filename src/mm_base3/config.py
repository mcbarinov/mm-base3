from __future__ import annotations

import importlib.metadata
import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_package_version(package: str) -> str:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return " unknown"


class BaseConfig(BaseSettings):
    app_name: str
    data_dir: Path
    access_token: str
    domain: str
    database_url: str
    debug: bool = False
    mm_base3_version: str = _get_package_version("mm-base3")
    app_version: str = _get_package_version("app")

    tags: list[str] = Field(default_factory=list)
    main_menu: dict[str, str] = Field(default_factory=dict)
    telegram_bot_help: str = "update me!"

    use_https: bool = True

    @property
    def logger_level(self) -> int:
        return logging.DEBUG if self.debug else logging.INFO

    @property
    def tags_metadata(self) -> list[dict[str, str]]:
        base = [
            {"name": "dconfig"},
            {"name": "dvalue"},
            {"name": "dlog"},
            {"name": "system"},
            {"name": "auth"},
            {"name": "base-ui"},
        ]
        app = [{"name": t} for t in self.tags]
        return app + base

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
