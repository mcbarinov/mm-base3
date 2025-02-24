from typing import cast

from litestar import Litestar

from app.core import Core
from app.jinja import custom_jinja
from app.routers.api_router import api_router
from app.routers.ui_router import ui_router
from mm_base3 import BaseCoreAny, init_server


def start() -> Litestar:
    core = Core()
    core.startup()
    return init_server(cast(BaseCoreAny, core), custom_jinja, ui_router, api_router)
