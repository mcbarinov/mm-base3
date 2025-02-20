import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from functools import partial
from typing import Any, NoReturn

from jinja2 import ChoiceLoader, Environment, PackageLoader
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.response import Template
from litestar.template import TemplateConfig
from markupsafe import Markup
from mm_std import utc_now

from mm_base3.base_core import BaseCore

type CallableAny = Callable[..., Any]


@dataclass
class CustomJinja:
    header_info: Callable[..., Markup] | None = None
    header_info_new_line: bool = False
    footer_info: Callable[..., Markup] | None = None
    filters: dict[str, CallableAny] | None = None
    globals: dict[str, CallableAny] | None = None


# [filters -->
# def dlog_data_truncate(data: object) -> str:
#     if not data:
#         return ""
#     res = json_dumps(data)
#     if len(res) > 100:
#         return res[:100] + "..."
#     return res


def timestamp(value: datetime | int | None, format_: str = "%Y-%m-%d %H:%M:%S") -> str:
    if isinstance(value, datetime):
        return value.strftime(format_)
    if isinstance(value, int):
        return datetime.fromtimestamp(value).strftime(format_)  # noqa: DTZ006
    return ""


def empty(value: object) -> object:
    return value if value else ""


def yes_no(
    value: object,
    is_colored: bool = True,
    hide_no: bool = False,
    none_is_false: bool = False,
    on_off: bool = False,
) -> Markup:
    clr = "black"
    if none_is_false and value is None:
        value = False

    if value is True:
        value = "on" if on_off else "yes"
        clr = "green"
    elif value is False:
        value = "" if hide_no else "off" if on_off else "no"
        clr = "red"
    elif value is None:
        value = ""
    if not is_colored:
        clr = "black"
    return Markup(f"<span style='color: {clr};'>{value}</span>")  # nosec


def json_url_encode(data: dict[str, object]) -> str:
    return json.dumps(data)


def nformat(
    value: str | float | Decimal | None,
    prefix: str = "",
    suffix: str = "",
    separator: str = "",
    hide_zero: bool = True,
    digits: int = 2,
) -> str:
    if value is None or value == "":
        return ""
    if float(value) == 0:
        if hide_zero:
            return ""
        return f"{prefix}0{suffix}"
    if float(value) > 1000:
        value = "".join(
            reversed([x + (separator if i and not i % 3 else "") for i, x in enumerate(reversed(str(int(value))))]),
        )
    else:
        value = round(value, digits)  # type: ignore[assignment, arg-type]

    return f"{prefix}{value}{suffix}"


def raise_(msg: str) -> NoReturn:
    raise RuntimeError(msg)


# <-- filter]


def init_jinja(core: BaseCore, custom_jinja: CustomJinja) -> TemplateConfig[JinjaTemplateEngine]:
    env = Environment(loader=ChoiceLoader([PackageLoader("mm_base3"), PackageLoader("app")]), autoescape=True)  # nosec
    # env.globals["get_flash_messages"] = get_flash_messages
    env.filters["timestamp"] = timestamp
    env.filters["dt"] = timestamp
    env.filters["empty"] = empty
    env.filters["yes_no"] = yes_no
    env.filters["nformat"] = nformat
    env.filters["n"] = nformat
    env.filters["json_url_encode"] = json_url_encode
    env.globals["config"] = core.config
    # env.globals["dconfig"] = app.dconfig
    # env.globals["dvalue"] = app.dvalue
    env.globals["now"] = utc_now
    env.globals["raise"] = raise_

    env.globals["confirm"] = Markup(""" onclick="return confirm('sure?')" """)
    if custom_jinja.filters:
        env.filters.update(custom_jinja.filters)
    if custom_jinja.globals:
        env.globals.update(custom_jinja.globals)

    header_info = custom_jinja.header_info if custom_jinja.header_info else lambda _: Markup("")
    footer_info = custom_jinja.footer_info if custom_jinja.footer_info else lambda _: Markup("")

    env.globals["header_info"] = partial(header_info, core)
    env.globals["footer_info"] = partial(footer_info, core)

    env.globals["header_info_new_line"] = custom_jinja.header_info_new_line

    return TemplateConfig(instance=JinjaTemplateEngine.from_environment(env))


def render_html(template_name: str, **kwargs: object) -> Template:
    return Template(template_name, context=kwargs, media_type="text/html")
