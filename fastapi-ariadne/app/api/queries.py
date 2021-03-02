from typing import Optional
from ariadne import QueryType, convert_kwargs_to_snake_case
from app.core.utils import MyGraphQLError

from app.db import db


@convert_kwargs_to_snake_case
async def resolve_items(obj, info, skip:Optional[int]=0, limit:Optional[int]=100):
    items = await db.get_items(skip=skip, limit=limit)

    return {
        "items": items
    }


@convert_kwargs_to_snake_case
async def resolve_item(obj, info, item_id):
    item = await db.get_item(item_id=item_id)

    if not item:
        raise MyGraphQLError(code=404, message=f"item id {item_id} not found")

    return {
        "success": True,
        "item": item
    }


query = QueryType()
query.set_field("items", resolve_items)
query.set_field("item", resolve_item)