"""Strawberry GraphQL FastAPI integration."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import strawberry

from .resolvers import Query
from .loaders import Loaders


# GraphQL request model
class GraphQLRequest(BaseModel):
    query: str
    variables: Optional[Dict[str, Any]] = None
    operation_name: Optional[str] = None


@asynccontextmanager
async def get_context():
    """Create context with loaders for each request."""
    loaders = Loaders()

    try:
        yield {
            "loaders": loaders,
        }
    finally:
        pass


async def context_getter() -> dict:
    """Context getter for GraphQL router."""
    async for ctx in get_context():
        return ctx


# Cache the schema globally (created once)
_schema = None

def create_strawberry_schema() -> strawberry.Schema:
    """Create Strawberry GraphQL schema (cached)."""
    global _schema
    if _schema is None:
        _schema = strawberry.Schema(query=Query)
    return _schema


def create_strawberry_app() -> FastAPI:
    """Create FastAPI app with Strawberry GraphQL."""
    schema = create_strawberry_schema()

    graphql_app = GraphQLRouter(
        schema,
        context_getter=context_getter,
    )

    app = FastAPI(title="Strawberry GraphQL Benchmark")
    app.include_router(graphql_app, prefix="/graphql")

    return app


# For benchmark direct execution
async def execute_query(query: str) -> dict:
    """Execute a GraphQL query directly (with cached schema)."""
    loaders = Loaders()
    schema = create_strawberry_schema()

    result = await schema.execute(
        query,
        context_value={
            "loaders": loaders,
        },
    )

    return {
        "data": result.data,
        "errors": [str(e) for e in result.errors] if result.errors else None,
    }
