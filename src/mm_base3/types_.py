from litestar.enums import RequestEncodingType
from litestar.params import Body

FormBody = Body(media_type=RequestEncodingType.URL_ENCODED)
