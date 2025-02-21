from pathlib import Path
from typing import cast

from bson import ObjectId
from litestar import Litestar, Router
from litestar.datastructures import State
from litestar.middleware import DefineMiddleware
from litestar.static_files import create_static_files_router
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from mm_base3 import CustomJinja
from mm_base3.auth import AuthMiddleware
from mm_base3.base_core import BaseCore
from mm_base3.jinja.jinja import init_jinja
from mm_base3.routers.api_method_router import APIMethodController
from mm_base3.routers.auth_router import AuthController
from mm_base3.routers.system_router import SystemController

TYPE_ENCODERS = {
    DeleteResult: lambda x: x.raw_result,
    InsertOneResult: lambda x: {"inserted_id": x.inserted_id, "acknowledged": x.acknowledged},
    UpdateResult: lambda x: x.raw_result,
    ObjectId: lambda x: str(x),
}

ASSETS = Path(__file__).parent.absolute() / "assets"


def init_server[CORE: BaseCore](core: CORE, custom_jinja: CustomJinja, ui_router: Router, api_router: Router) -> Litestar:
    def core_dep(state: State) -> CORE:
        return cast(CORE, state.get("core"))

    auth_mw = DefineMiddleware(AuthMiddleware, exclude="/auth/")
    return Litestar(
        route_handlers=[
            create_static_files_router(path="/assets", directories=[ASSETS]),
            APIMethodController,
            AuthController,
            SystemController,
            ui_router,
            api_router,
        ],
        state=State({"core": core}),
        dependencies={"core": core_dep},
        middleware=[auth_mw],
        template_config=init_jinja(core, custom_jinja),
        type_encoders=TYPE_ENCODERS,
        on_shutdown=[lambda: core.shutdown()],
        debug=core.config.debug,
    )
