from typing import TypeVar

from litestar.enums import RequestEncodingType
from litestar.params import Body

from mm_base3 import BaseAppConfig
from mm_base3.base_db import BaseDb
from mm_base3.services.dconfig_service import DConfigDict

FormBody = Body(media_type=RequestEncodingType.URL_ENCODED)


APP_CONFIG_T = TypeVar("APP_CONFIG_T", bound=BaseAppConfig)
DCONFIG_T = TypeVar("DCONFIG_T", bound=DConfigDict)
DB_T = TypeVar("DB_T", bound=BaseDb)
