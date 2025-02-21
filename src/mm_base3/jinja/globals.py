from functools import partial
from typing import NoReturn

from markupsafe import Markup
from mm_std import utc_now

from mm_base3.base_core import BaseCore
from mm_base3.jinja import CustomJinja


def raise_(msg: str) -> NoReturn:
    raise RuntimeError(msg)


def base_globals(core: BaseCore, custom_jinja: CustomJinja) -> dict[str, object]:
    header_info = custom_jinja.header_info if custom_jinja.header_info else lambda _: Markup("")
    footer_info = custom_jinja.footer_info if custom_jinja.footer_info else lambda _: Markup("")
    return {
        "raise": raise_,
        "config": core.config,
        "now": utc_now,
        "confirm": Markup(""" onclick="return confirm('sure?')" """),
        "header_info": partial(header_info, core),
        "footer_info": partial(footer_info, core),
        "header_info_new_line": custom_jinja.header_info_new_line,
    }
