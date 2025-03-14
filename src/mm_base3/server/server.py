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
from mm_std import Err, Ok, Result
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from mm_base3 import CustomJinja
from mm_base3.core.core import BaseCore, DB_co, DCONFIG_co, DVALUE_co
from mm_base3.core.errors import UserError
from mm_base3.server import utils
from mm_base3.server.auth import AuthMiddleware
from mm_base3.server.config import BaseServerConfig
from mm_base3.server.jinja import init_jinja
from mm_base3.server.routers.api_method_router import APIMethodController
from mm_base3.server.routers.auth_router import AuthController
from mm_base3.server.routers.system_api_router import system_api_router
from mm_base3.server.routers.system_ui_router import system_ui_router

TYPE_ENCODERS = {
    DeleteResult: lambda x: x.raw_result,
    InsertOneResult: lambda x: {"inserted_id": x.inserted_id, "acknowledged": x.acknowledged},
    UpdateResult: lambda x: x.raw_result,
    ObjectId: lambda x: str(x),
    Result: lambda x: {"ok": x.ok, "err": x.err, "data": x.data},
    Ok: lambda x: {"ok": x.ok, "data": x.data},
    Err: lambda x: {"err": x.err, "data": x.data},
}

ASSETS = Path(__file__).parent.absolute() / "assets"


def init_server(
    core: BaseCore[DCONFIG_co, DVALUE_co, DB_co],
    server_config: BaseServerConfig,
    custom_jinja: CustomJinja,
    ui_router: Router,
    api_router: Router,
) -> Litestar:
    logging.getLogger("httpx").setLevel(logging.WARNING)

    async def core_dep(state: State) -> BaseCore[DCONFIG_co, DVALUE_co, DB_co]:
        return cast(BaseCore[DCONFIG_co, DVALUE_co, DB_co], state.get("core"))

    async def server_config_dep(state: State) -> BaseServerConfig:
        return cast(BaseServerConfig, state.get("server_config"))

    auth_mw = DefineMiddleware(AuthMiddleware, exclude="/auth/")
    template_config = init_jinja(core, server_config, custom_jinja)
    flash_plugin = FlashPlugin(config=FlashConfig(template_config=template_config))

    return Litestar(
        route_handlers=[
            create_static_files_router(path="/assets", directories=[ASSETS]),
            APIMethodController,
            AuthController,
            system_ui_router,
            system_api_router,
            ui_router,
            api_router,
        ],
        state=State({"core": core, "server_config": server_config}),
        dependencies={"core": core_dep, "server_config": server_config_dep},
        plugins=[flash_plugin],
        middleware=[ServerSideSessionConfig().middleware, auth_mw],
        template_config=template_config,
        type_encoders=TYPE_ENCODERS,
        on_shutdown=[lambda: core.shutdown()],
        exception_handlers={Exception: all_exceptions_handler},
        debug=core.core_config.debug,
        openapi_config=OpenAPIConfig(
            title=core.core_config.app_name,
            version=utils.get_package_version("app"),
            tags=[*[Tag(name=t) for t in server_config.tags], Tag(name="system", description="mm-base3 system api")],
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

        if not core.core_config.debug:
            message = "error"

    return Response(media_type=MediaType.TEXT, content=message, status_code=code)
