from typing import Annotated, Any, TypeVar

from litestar import Request
from litestar.enums import RequestEncodingType
from litestar.params import Body

from mm_base3 import BaseAppConfig
from mm_base3.base_db import BaseDb
from mm_base3.dconfig import DConfigDict

FormBody = Body(media_type=RequestEncodingType.URL_ENCODED)

FormData = Annotated[dict[str, str], Body(media_type=RequestEncodingType.URL_ENCODED)]

type RequestAny = Request[Any, Any, Any]

APP_CONFIG_T = TypeVar("APP_CONFIG_T", bound=BaseAppConfig)
DCONFIG_T = TypeVar("DCONFIG_T", bound=DConfigDict)
DB_T = TypeVar("DB_T", bound=BaseDb)
