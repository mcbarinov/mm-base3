from markupsafe import Markup

from app.core import Core
from app.db import DataStatus
from mm_base3 import CustomJinja


def data_status(status: DataStatus) -> Markup:
    color = "black"
    if status == DataStatus.OK:
        color = "green"
    elif status == DataStatus.ERROR:
        color = "red"
    return Markup(f"<span style='color: {color};'>{status.value}</span>")


def header_info(_core: Core) -> Markup:
    info = "<span style='color: red'>bbb</span>"
    return Markup(info)


def footer_info(_core: Core) -> Markup:
    info = ""
    return Markup(info)


custom_jinja = CustomJinja(
    header_info=header_info,
    header_info_new_line=True,
    footer_info=footer_info,
    filters={"data_status": data_status},
)
