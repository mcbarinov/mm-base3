from litestar.response import Template


def render_html(template_name: str, **kwargs: object) -> Template:
    return Template(template_name, context=kwargs, media_type="text/html")


def process_form_with_checkboxes(data: dict[str, object]) -> dict[str, str]:
    """Process form data with checkboxes and return only checked values.
    The hidden input with the same name goes before checkbox field."""
    result = {}
    for key, value in data.items():
        if isinstance(value, list):
            result[key] = value[-1]
        else:
            result[key] = value
    return result
