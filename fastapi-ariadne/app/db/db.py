
from app.core.utils import MyGraphQLError
import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union

import sqlalchemy as sa
from app.core.config import settings

database = databases.Database(
    settings.SQLALCHEMY_DATABASE_URI, 
    ssl=settings.SQLALCHEMY_DATABASE_SSL, 
    min_size=settings.SQLALCHEMY_DATABASE_MIN_POOL, 
    max_size=settings.SQLALCHEMY_DATABASE_MAX_POOL
)

metadata = sa.MetaData()

users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("email", sa.String, nullable=False),
    sa.Column("hashed_password", sa.String, nullable=False),
    sa.Column("created_date", sa.DateTime)
)

items = sa.Table(
    "items",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("title", sa.String, nullable=False),
    sa.Column("description", sa.String, nullable=True),
    sa.Column("owner_id", sa.Integer, nullable=False),
    sa.Column("created_date", sa.DateTime)
)

engine = sa.create_engine(
    settings.SQLALCHEMY_DATABASE_URI, connect_args={}, echo=True
)
metadata.create_all(engine)


async def get_user_by_email(email: str) -> Optional[Dict]:
    query = users.select().where(users.c.email == email)
    user = await database.fetch_one(query=query)
    return dict(user) if user else None


async def get_user_by_id(user_id: int) -> Optional[Dict]:
    query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(query=query)
    return dict(user) if user else None


async def get_items(skip:Optional[int]=0, limit:Optional[int]=100) -> Optional[Dict]:
    query = items.select(offset=skip, limit=limit)
    result = await database.fetch_all(query=query)
    return [dict(item) for item in result] if result else None


async def get_item(item_id: int) -> Optional[Dict]:
    query = items.select().where(items.c.id == int(item_id))
    result = await database.fetch_one(query=query)
    return dict(result) if result else None


async def create_user(email: str, hashed_password: str) -> int:
    fetched_user = await get_user_by_email(email)
    if fetched_user:
        raise MyGraphQLError(code=409, message="Email already registered")

    params = {
        "email":email,
        "hashed_password": hashed_password
    }
    query = users.insert()
    user_id = await database.execute(query=query, values=params)
    return user_id


async def create_item(title: str, description: str, owner_id: str) -> int:
    params = {
        "title":title,
        "description":description,
        "owner_id": owner_id
    }
    query = items.insert()
    item_id = await database.execute(query=query, values=params)
    return item_id