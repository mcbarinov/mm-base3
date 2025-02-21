from litestar.response import Template


def render_html(template_name: str, **kwargs: object) -> Template:
    return Template(template_name, context=kwargs, media_type="text/html")
