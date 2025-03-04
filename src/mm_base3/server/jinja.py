from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any

import mm_jinja
from jinja2 import ChoiceLoader, PackageLoader
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template import TemplateConfig
from markupsafe import Markup
from mm_mongo import json_dumps

from mm_base3.core.core import BaseCore, DB_co, DCONFIG_co, DVALUE_co
from mm_base3.server import utils
from mm_base3.server.config import BaseServerConfig


def system_log_data_truncate(data: object) -> str:
    if not data:
        return ""
    res = json_dumps(data)
    if len(res) > 100:
        return res[:100] + "..."
    return res


@dataclass
class CustomJinja:
    header_info: Callable[..., Markup] | None = None
    header_info_new_line: bool = False
    footer_info: Callable[..., Markup] | None = None
    filters: dict[str, Callable[..., Any]] | None = None
    globals: dict[str, Any] | None = None


def init_jinja(
    core: BaseCore[DCONFIG_co, DVALUE_co, DB_co], server_config: BaseServerConfig, custom_jinja: CustomJinja
) -> TemplateConfig[JinjaTemplateEngine]:
    loader = ChoiceLoader([PackageLoader("mm_base3.server"), PackageLoader("app.server")])

    header_info = custom_jinja.header_info if custom_jinja.header_info else lambda _: Markup("")
    footer_info = custom_jinja.footer_info if custom_jinja.footer_info else lambda _: Markup("")
    custom_filters: dict[str, Callable[..., Any]] = {"system_log_data_truncate": system_log_data_truncate}
    custom_globals: dict[str, Any] = {
        "core_config": core.core_config,
        "server_config": server_config,
        "dconfig": core.dconfig,
        "dvalue": core.dvalue,
        "confirm": Markup(""" onclick="return confirm('sure?')" """),
        "header_info": partial(header_info, core),
        "footer_info": partial(footer_info, core),
        "header_info_new_line": custom_jinja.header_info_new_line,
        "app_version": utils.get_package_version("app"),
        "mm_base3_version": utils.get_package_version("mm_base3"),
    }

    if custom_jinja.globals:
        custom_globals |= custom_jinja.globals
    if custom_jinja.filters:
        custom_filters |= custom_jinja.filters

    env = mm_jinja.init_jinja(loader, custom_globals=custom_globals, custom_filters=custom_filters)

    return TemplateConfig(instance=JinjaTemplateEngine.from_environment(env))
