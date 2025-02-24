from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from logging import Logger

from mm_base3.base_db import BaseDb
from mm_base3.config import BaseAppConfig
from mm_base3.services.dconfig_service import DConfigDict


@dataclass
class BaseServiceParams[APP_CONFIG: BaseAppConfig, DCONFIG: DConfigDict, DB: BaseDb]:
    app_config: APP_CONFIG
    dconfig: DCONFIG
    db: DB
    logger: Logger
    dlog: Callable[[str, object], None]


class BaseService[APP_CONFIG: BaseAppConfig, DCONFIG: DConfigDict, DB: BaseDb]:
    def __init__(self, base_params: BaseServiceParams[APP_CONFIG, DCONFIG, DB]) -> None:
        self.app_config = base_params.app_config
        self.dconfig = base_params.dconfig
        self.db = base_params.db
        self.logger = base_params.logger
        self.dlog = base_params.dlog
