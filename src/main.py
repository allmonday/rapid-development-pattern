from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute
import src.db as db
import src.router.sample_1.router as s1_router
import src.router.sample_2.router as s2_router
import src.router.sample_3.router as s3_router
import src.router.sample_4.router as s4_router
import src.router.sample_5.router as s5_router
import src.router.sample_6.router as s6_router
import src.router.sample_7.router as s7_router
import src.router.demo.router as demo_router
from fastapi_voyager import create_voyager
from src.services.er_diagram import BaseEntity
from pydantic_resolve import config_global_resolver
from fastapi.openapi.utils import get_openapi
from typing import List
import json

diagram = BaseEntity.get_diagram()

config_global_resolver(diagram)

async def startup():
    print('start')
    await db.init()
    await db.prepare()
    print('done')

async def shutdown():
    print('end start')
    await db.engine.dispose()
    print('end done')

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()


app = FastAPI(debug=True, lifespan=lifespan)

def custom_openapi():
    """自定义 OpenAPI schema 生成，修改 response_model 的 required 字段"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        servers=app.servers,
    )
    # 收集所有在 responses 中引用的 schema 名称
    response_schema_refs = set()

    def collect_schema_refs_from_schema(schema, refs_set):
        """递归收集 schema 中的所有 $ref"""
        if isinstance(schema, dict):
            if "$ref" in schema:
                # 从 "#/components/schemas/SchemaName" 中提取 SchemaName
                ref_path = schema["$ref"]
                if ref_path.startswith("#/components/schemas/"):
                    schema_name = ref_path.split("/")[-1]
                    refs_set.add(schema_name)
            # 递归处理嵌套的 schema
            for value in schema.values():
                collect_schema_refs_from_schema(value, refs_set)
        elif isinstance(schema, list):
            for item in schema:
                collect_schema_refs_from_schema(item, refs_set)

    # 遍历 paths 中的所有 endpoint
    for path_data in openapi_schema.get("paths", {}).values():
        for method_data in path_data.values():
            if isinstance(method_data, dict) and "responses" in method_data:
                # 遍历该 endpoint 的所有 responses
                for response in method_data["responses"].values():
                    if "content" in response:
                        for content_data in response["content"].values():
                            if "schema" in content_data:
                                # 收集 response schema 中的所有 $ref
                                collect_schema_refs_from_schema(
                                    content_data["schema"],
                                    response_schema_refs
                                )

    # 只修改在 responses 中引用的 schemas
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        for schema_name, schema in openapi_schema["components"]["schemas"].items():
            # 只处理在 responses 中引用的 schema
            if schema_name in response_schema_refs and "properties" in schema:
                # 将所有字段名添加到 required
                all_fields = list(schema["properties"].keys())
                schema["required"] = all_fields

    app.openapi_schema = openapi_schema

app.openapi = custom_openapi


app.include_router(s1_router.route)
app.include_router(s2_router.route)
app.include_router(s3_router.route)
app.include_router(s4_router.route)
app.include_router(s5_router.route)
app.include_router(s6_router.route)
app.include_router(s7_router.route)
app.include_router(demo_router.route)

app.mount('/voyager', 
          create_voyager(
            app, 
            er_diagram=diagram,
            module_color={'src.services': 'purple'}, 
            module_prefix='src.services', 
            swagger_url="/docs",
            ga_id="G-R64S7Q49VL",
            initial_page_policy='first',
            online_repo_url='https://github.com/allmonday/composition-oriented-development-pattern/blob/master',
            enable_pydantic_resolve_meta=True))


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'

use_route_names_as_operation_ids(app)
