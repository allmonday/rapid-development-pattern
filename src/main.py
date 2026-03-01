from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
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
from pydantic_resolve.graphql import GraphQLHandler, SchemaBuilder

diagram = BaseEntity.get_diagram()

config_global_resolver(diagram)

# GraphQL handler and schema builder
graphql_handler = GraphQLHandler(diagram, enable_from_attribute_in_type_adapter=True)
graphql_schema_builder = SchemaBuilder(diagram)

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

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(s1_router.route)
app.include_router(s2_router.route)
app.include_router(s3_router.route)
app.include_router(s4_router.route)
app.include_router(s5_router.route)
app.include_router(s6_router.route)
app.include_router(s7_router.route)
app.include_router(demo_router.route)


# GraphQL request model
class GraphQLRequest(BaseModel):
    query: str
    variables: Optional[Dict[str, Any]] = None
    operation_name: Optional[str] = None


# GraphQL endpoints
GRAPHIQL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>GraphiQL</title>
  <style>
    body { margin: 0; }
    #graphiql { height: 100dvh; }
    .loading {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2rem;
    }
  </style>
  <link rel="stylesheet" href="https://esm.sh/graphiql/dist/style.css" />
  <link rel="stylesheet" href="https://esm.sh/@graphiql/plugin-explorer/dist/style.css" />
  <script type="importmap">
    {
      "imports": {
        "react": "https://esm.sh/react@19.1.0",
        "react/jsx-runtime": "https://esm.sh/react@19.1.0/jsx-runtime",
        "react-dom": "https://esm.sh/react-dom@19.1.0",
        "react-dom/client": "https://esm.sh/react-dom@19.1.0/client",
        "@emotion/is-prop-valid": "data:text/javascript,",
        "graphiql": "https://esm.sh/graphiql?standalone&external=react,react-dom,@graphiql/react,graphql",
        "graphiql/": "https://esm.sh/graphiql/",
        "@graphiql/plugin-explorer": "https://esm.sh/@graphiql/plugin-explorer?standalone&external=react,@graphiql/react,graphql",
        "@graphiql/react": "https://esm.sh/@graphiql/react?standalone&external=react,react-dom,graphql,@emotion/is-prop-valid",
        "@graphiql/toolkit": "https://esm.sh/@graphiql/toolkit?standalone&external=graphql",
        "graphql": "https://esm.sh/graphql@16.11.0"
      }
    }
  </script>
</head>
<body>
  <div id="graphiql">
    <div class="loading">Loading…</div>
  </div>
  <script type="module">
    import React from 'react';
    import ReactDOM from 'react-dom/client';
    import { GraphiQL, HISTORY_PLUGIN } from 'graphiql';
    import { createGraphiQLFetcher } from '@graphiql/toolkit';
    import { explorerPlugin } from '@graphiql/plugin-explorer';

    const fetcher = createGraphiQLFetcher({ url: '/graphql' });
    const plugins = [HISTORY_PLUGIN, explorerPlugin()];

    function App() {
      return React.createElement(GraphiQL, {
        fetcher: fetcher,
        plugins: plugins,
      });
    }

    const container = document.getElementById('graphiql');
    const root = ReactDOM.createRoot(container);
    root.render(React.createElement(App));
  </script>
</body>
</html>
"""


@app.get("/graphql", response_class=HTMLResponse)
async def graphiql_playground():
    """GraphiQL interactive playground"""
    return GRAPHIQL_HTML


@app.post("/graphql")
async def graphql_endpoint(req: GraphQLRequest):
    """GraphQL query endpoint"""
    return await graphql_handler.execute(
        query=req.query,
    )


@app.get("/schema", response_class=PlainTextResponse)
async def graphql_schema():
    """GraphQL Schema SDL endpoint"""
    return graphql_schema_builder.build_schema()


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
