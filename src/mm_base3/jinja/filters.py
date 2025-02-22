import json
from datetime import datetime
from decimal import Decimal

from markupsafe import Markup
from mm_mongo import json_dumps


def timestamp(value: datetime | int | None, format_: str = "%Y-%m-%d %H:%M:%S") -> str:
    if isinstance(value, datetime):
        return value.strftime(format_)
    if isinstance(value, int):
        return datetime.fromtimestamp(value).strftime(format_)  # noqa: DTZ006
    return ""


def empty(value: object) -> object:
    return value if value else ""


def yes_no(
    value: object, is_colored: bool = True, hide_no: bool = False, none_is_false: bool = False, on_off: bool = False
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


def json_url_encode(data: dict[str, object]) -> str:
    return json.dumps(data)


def system_log_data_truncate(data: object) -> str:
    if not data:
        return ""
    res = json_dumps(data)
    if len(res) > 100:
        return res[:100] + "..."
    return res


BASE_FILTERS = {
    "timestamp": timestamp,
    "dt": timestamp,
    "empty": empty,
    "yes_no": yes_no,
    "nformat": nformat,
    "n": nformat,
    "json_url_encode": json_url_encode,
    "system_log_data_truncate": system_log_data_truncate,
}
