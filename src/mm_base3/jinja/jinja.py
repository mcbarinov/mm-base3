from jinja2 import ChoiceLoader, Environment, PackageLoader
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template import TemplateConfig

from mm_base3.base_core import BaseCoreAny
from mm_base3.jinja import CustomJinja
from mm_base3.jinja.filters import BASE_FILTERS
from mm_base3.jinja.globals import base_globals


def init_jinja(core: BaseCoreAny, custom_jinja: CustomJinja) -> TemplateConfig[JinjaTemplateEngine]:
    env = Environment(loader=ChoiceLoader([PackageLoader("mm_base3"), PackageLoader("app")]), autoescape=True)  # nosec
    env.filters |= BASE_FILTERS
    env.globals |= base_globals(core, custom_jinja)

    if custom_jinja.filters:
        env.filters |= custom_jinja.filters
    if custom_jinja.globals:
        env.globals |= custom_jinja.globals

    return TemplateConfig(instance=JinjaTemplateEngine.from_environment(env))
