from litestar import Litestar

from app.config import AppConfig
from app.core import Core
from app.jinja import custom_jinja
from app.routers.api_router import api_router
from app.routers.ui_router import ui_router
from mm_base3 import init_server


def start() -> Litestar:
    # noinspection PyArgumentList
    config = AppConfig()
    core = Core(config)
    core.startup()
    return init_server(core, custom_jinja, ui_router, api_router)
