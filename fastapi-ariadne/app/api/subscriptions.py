import asyncio
import aio_pika

from typing import Optional
from ariadne import SubscriptionType, convert_kwargs_to_snake_case
from graphql import GraphQLError
from graphql.type import GraphQLResolveInfo

from app.core.store import queues
from app.core import security
from app.core.utils import MyGraphQLError
from app.core import config
from app.db import rabbit

subscription = SubscriptionType()


@convert_kwargs_to_snake_case
@subscription.field("reviewItem")
async def review_item_resolver(review_item, info: GraphQLResolveInfo, token:str):
    return {"id": review_item}


@convert_kwargs_to_snake_case
@subscription.source("reviewItem")
async def review_item_source(obj, info: GraphQLResolveInfo, token:str):
    user = await security.get_current_user_by_auth_header(token)
    if not user:
        raise MyGraphQLError(code=401, message="User not authenticated")

    while(True):
        item_id = await rabbit.consumeItem()
        if item_id:
            yield item_id
        else:
            return