from pathlib import Path
from typing import cast

from bson import ObjectId
from litestar import Litestar, Router
from litestar.datastructures import State
from litestar.static_files import create_static_files_router
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from mm_base3 import CustomJinja
from mm_base3.base_core import BaseCore
from mm_base3.jinja.jinja import init_jinja
from mm_base3.routers.api_method_router import APIMethodController

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

    return Litestar(
        route_handlers=[
            create_static_files_router(path="/assets", directories=[ASSETS]),
            APIMethodController,
            ui_router,
            api_router,
        ],
        state=State({"core": core}),
        dependencies={"core": core_dep},
        template_config=init_jinja(core, custom_jinja),
        type_encoders=TYPE_ENCODERS,
        on_shutdown=[lambda: core.shutdown()],
        debug=core.config.debug,
    )
