from litestar import Litestar
from pydantic import Field

from app.core import Core
from app.jinja import custom_jinja
from app.routers.api_router import api_router
from app.routers.ui_router import ui_router
from mm_base3 import BaseConfig, init_server


class AppConfig(BaseConfig):
    tags: list[str] = Field(["data"])
    main_menu: dict[str, str] = Field({"/data": "data"})
    telegram_bot_help: str = """
/first_command - bla bla1
/second_command - bla bla2
"""


def start() -> Litestar:
    # noinspection PyArgumentList
    config = AppConfig()
    core = Core(config)
    core.startup()
    return init_server(core, custom_jinja, ui_router, api_router)
