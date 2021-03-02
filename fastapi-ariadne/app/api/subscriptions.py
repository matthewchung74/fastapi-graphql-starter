import asyncio

from typing import Optional
from ariadne import SubscriptionType, convert_kwargs_to_snake_case
from graphql import GraphQLError
from graphql.type import GraphQLResolveInfo

from app.core.store import queues
from app.core import security
from app.core.utils import MyGraphQLError


subscription = SubscriptionType()


@convert_kwargs_to_snake_case
@subscription.field("new_item")
async def new_item_resolver(new_item, info: GraphQLResolveInfo, token:str):
    return {"id": new_item}

@convert_kwargs_to_snake_case
@subscription.source("new_item")
async def new_item_source(obj, info: GraphQLResolveInfo, token:str):
    user = await security.get_current_user_by_auth_header(token)
    if not user:
        raise MyGraphQLError(code=401, message="User not authenticated")

    queue = asyncio.Queue()
    queues.append(queue)
    try:
        while True:
            item_id = await queue.get()
            queue.task_done()
            yield item_id
    except asyncio.CancelledError:
        queues.remove(queue)
        raise