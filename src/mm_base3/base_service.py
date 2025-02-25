from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from logging import Logger

from mm_base3.base_db import BaseDb
from mm_base3.config import BaseAppConfig
from mm_base3.dconfig import DConfigDict
from mm_base3.dvalue import DValueDict


@dataclass
class BaseServiceParams[APP_CONFIG_T: BaseAppConfig, DCONFIG_T: DConfigDict, DVALUE_T: DValueDict, DB_T: BaseDb]:
    app_config: APP_CONFIG_T
    dconfig: DCONFIG_T
    dvalue: DVALUE_T
    db: DB_T
    logger: Logger
    dlog: Callable[[str, object], None]


class BaseService[APP_CONFIG_T: BaseAppConfig, DCONFIG_T: DConfigDict, DVALUE_T: DValueDict, DB_T: BaseDb]:
    def __init__(self, base_params: BaseServiceParams[APP_CONFIG_T, DCONFIG_T, DVALUE_T, DB_T]) -> None:
        self.app_config = base_params.app_config
        self.dconfig = base_params.dconfig
        self.dvalue = base_params.dvalue
        self.db = base_params.db
        self.logger = base_params.logger
        self.dlog = base_params.dlog
