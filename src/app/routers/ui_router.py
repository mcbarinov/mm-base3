from litestar import Controller, Router, get, post
from litestar.plugins.flash import flash
from litestar.response import Redirect, Template
from mm_std import Err, Ok, Result

from app.core import Core
from mm_base3 import FormData, RequestAny, render_html


class PagesController(Controller):
    path = "/"
    tags = ["ui"]

    @get()
    def index(self) -> Template:
        return render_html("index.j2")

    @get("/data")
    def data(self, core: Core) -> Template:
        return render_html("data.j2", data_list=core.db.data.find({}))

    @get("/test")
    def test(self) -> Template:
        return render_html("test.j2", zero=0)


class ActionsController(Controller):
    path = "/"

    @post("/inc-data/{id:str}")
    def inc_data(self, core: Core, id: str, data: FormData, request: RequestAny) -> Redirect:
        value = int(data["value"])
        core.db.data.update_one({"_id": id}, {"$inc": {"value": value}})
        flash(request, f"Data {id} incremented by {value}", "success")
        return Redirect("/data")

    @get("/test-result-ok")
    def test_result_ok(self) -> Result[str]:
        return Ok("it works")

    @get("/test-result-err")
    def test_result_err(self) -> Result[str]:
        return Err("bla bla", data=["ssss", 123])


ui_router = Router(path="/", tags=["ui"], route_handlers=[PagesController, ActionsController], include_in_schema=False)
