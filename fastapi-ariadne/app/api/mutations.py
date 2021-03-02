from datetime import timedelta

from ariadne import MutationType, convert_kwargs_to_snake_case
from graphql import GraphQLError

from app.db import db
from app.core import security
from app.core import config
from app.core.utils import MyGraphQLError

from app.core import store

@convert_kwargs_to_snake_case
async def resolve_create_item(obj, info, title, description):
    user = await security.get_current_user_by_info(info)
    if not user:
        raise MyGraphQLError(code=401, message="User not authenticated")
    item_id = await db.create_item(title=title, description=description, owner_id=user["id"])

    for queue in store.queues:
        await queue.put(item_id)

    return {
        "id": item_id
    }


@convert_kwargs_to_snake_case
async def resolve_create_user(obj, info, email, password):
    hashed_password = security.get_password_hash(password)
    params = {'email':email, 'hashed_password': hashed_password}
    query = db.users.insert()
    result = await db.database.execute(query=query, values=params)

    return {
        "id": result
    }


@convert_kwargs_to_snake_case
async def resolve_login(obj, info, email, password):
    fetched_user = await db.get_user_by_email(email=email)
    if not fetched_user:
        raise MyGraphQLError(code=404, message="Email not found")
        
    hashed_password = fetched_user["hashed_password"]
    is_authenticated = security.verify_password(password, hashed_password)

    if not is_authenticated:
        raise MyGraphQLError(code=401, message="Invalid password")

    access_token_expires = timedelta(seconds=config.settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    token = security.create_access_token(fetched_user["id"], expires_delta=access_token_expires)
    return {"token":token}


mutation = MutationType()
mutation.set_field("createItem", resolve_create_item)
mutation.set_field("createUser", resolve_create_user)
mutation.set_field("createToken", resolve_login)
