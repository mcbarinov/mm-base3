from litestar import Litestar

from app.core.core import Core
from app.server.jinja import custom_jinja
from app.server.routers.api_router import api_router
from app.server.routers.ui_router import ui_router
from mm_base3 import init_server


def start() -> Litestar:
    core = Core()
    core.startup()
    return init_server(core, custom_jinja, ui_router, api_router)
