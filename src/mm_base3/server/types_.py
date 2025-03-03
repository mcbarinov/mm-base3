from typing import Annotated, Any

from litestar import Request
from litestar.enums import RequestEncodingType
from litestar.params import Body

FormBody = Body(media_type=RequestEncodingType.URL_ENCODED)

FormData = Annotated[dict[str, str], Body(media_type=RequestEncodingType.URL_ENCODED)]

type RequestAny = Request[Any, Any, Any]
