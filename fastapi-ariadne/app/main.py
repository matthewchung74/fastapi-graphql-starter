import sys, traceback

from typing import Optional
from graphql.error.graphql_error import GraphQLError
from starlette.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json

from fastapi import FastAPI, Request
from starlette.datastructures import URL

from ariadne import  load_schema_from_path, make_executable_schema, snake_case_fallback_resolvers
from ariadne.constants import PLAYGROUND_HTML
from ariadne.asgi import GraphQL
from ariadne import format_error, graphql_sync

from app.api.queries import query
from app.api.mutations import mutation
from app.api.subscriptions import subscription

from app.core import security
from app.db import db

app = FastAPI()

def my_format_error(error: GraphQLError, debug: bool = False) -> dict:
    if debug:
        return format_error(error, debug)

    formatted = error.formatted
    formatted["message"] = error.args[0]
    return formatted


@app.on_event("startup")
async def startup():
    await db.database.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.database.disconnect()


type_defs = load_schema_from_path("schema.graphql")
resolvers = [query, mutation, subscription]
schema = make_executable_schema(type_defs, resolvers, snake_case_fallback_resolvers)
graphQL = GraphQL(
    schema, 
    error_formatter=my_format_error, 
    middleware=[],
    debug=False)


app.mount("/", graphQL)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, loop="asyncio")