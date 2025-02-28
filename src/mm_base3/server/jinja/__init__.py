from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from markupsafe import Markup


@dataclass
class CustomJinja:
    header_info: Callable[..., Markup] | None = None
    header_info_new_line: bool = False
    footer_info: Callable[..., Markup] | None = None
    filters: dict[str, Callable[..., Any]] | None = None
    globals: dict[str, Callable[..., Any]] | None = None
