from __future__ import annotations

from dataclasses import dataclass
from logging import Logger

from mm_base3.base_db import BaseDb
from mm_base3.config import BaseConfig


@dataclass
class BaseServiceParams[CONFIG: BaseConfig, DB: BaseDb]:
    logger: Logger
    config: CONFIG
    db: DB


class BaseService[CONFIG: BaseConfig, DB: BaseDb]:
    def __init__(self, base_params: BaseServiceParams[CONFIG, DB]) -> None:
        self.logger = base_params.logger
        self.config = base_params.config
        self.db = base_params.db
