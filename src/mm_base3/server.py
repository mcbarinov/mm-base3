import logging
import traceback
from pathlib import Path
from typing import Any, cast

from bson import ObjectId
from litestar import Litestar, MediaType, Request, Response, Router
from litestar.datastructures import State
from litestar.middleware import DefineMiddleware
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Tag
from litestar.plugins.flash import FlashConfig, FlashPlugin
from litestar.static_files import create_static_files_router
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from mm_base3 import CustomJinja
from mm_base3.auth import AuthMiddleware
from mm_base3.base_core import BaseCoreAny
from mm_base3.errors import UserError
from mm_base3.jinja.jinja import init_jinja
from mm_base3.routers.api_method_router import APIMethodController
from mm_base3.routers.auth_router import AuthController
from mm_base3.routers.system_router import system_router

TYPE_ENCODERS = {
    DeleteResult: lambda x: x.raw_result,
    InsertOneResult: lambda x: {"inserted_id": x.inserted_id, "acknowledged": x.acknowledged},
    UpdateResult: lambda x: x.raw_result,
    ObjectId: lambda x: str(x),
}

ASSETS = Path(__file__).parent.absolute() / "assets"


def init_server(core: BaseCoreAny, custom_jinja: CustomJinja, ui_router: Router, api_router: Router) -> Litestar:
    logging.getLogger("httpx").setLevel(logging.WARNING)

    def core_dep(state: State) -> BaseCoreAny:
        return cast(BaseCoreAny, state.get("core"))

    auth_mw = DefineMiddleware(AuthMiddleware, exclude="/auth/")
    template_config = init_jinja(core, custom_jinja)
    flash_plugin = FlashPlugin(config=FlashConfig(template_config=template_config))

    return Litestar(
        route_handlers=[
            create_static_files_router(path="/assets", directories=[ASSETS]),
            APIMethodController,
            AuthController,
            system_router,
            ui_router,
            api_router,
        ],
        state=State({"core": core}),
        dependencies={"core": core_dep},
        plugins=[flash_plugin],
        middleware=[ServerSideSessionConfig().middleware, auth_mw],
        template_config=template_config,
        type_encoders=TYPE_ENCODERS,
        on_shutdown=[lambda: core.shutdown()],
        exception_handlers={Exception: all_exceptions_handler},
        debug=core.app_config.debug,
        openapi_config=OpenAPIConfig(
            title=core.app_config.app_name,
            version=core.app_config.app_version,
            tags=[*[Tag(name=t) for t in core.app_config.tags], Tag(name="system", description="mm-base3 system api")],
        ),
    )


def all_exceptions_handler(req: Request[Any, Any, Any], exc: Exception) -> Response[str]:
    message = str(exc)
    code = getattr(exc, "status_code", HTTP_500_INTERNAL_SERVER_ERROR)
    hide_stacktrace = isinstance(exc, UserError)
    if code in [400, 401, 403, 404, 405]:
        hide_stacktrace = True

    core = req.app.state.get("core")
    if core is not None:
        if not hide_stacktrace:
            core.logger.exception(exc)
            message += "\n\n" + traceback.format_exc()

        if not core.app_config.debug:
            message = "error"

    return Response(media_type=MediaType.TEXT, content=message, status_code=code)
