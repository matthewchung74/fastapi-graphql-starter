import uvicorn
import pytest
from multiprocessing import Process
import time
import string 
import random 

from app.main import app, schema
from app.db import db


def run_server():
    uvicorn.run(app)

@pytest.fixture(scope="module")
def host():
    return "127.0.0.1:8000"


@pytest.fixture(scope="module")
def credentials():
    random_string = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 4)) 

    email = f"unitest_{random_string}@bar.com"
    return {
        "email":email, 
        "password":"password"
    }


@pytest.fixture(scope="module")
def server(credentials):
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start() 
    time.sleep(2)
    yield

    # cleanup
    conn = db.engine
    query = db.users.select().where(db.users.c.email == credentials["email"])
    user_result = next(conn.execute(query))

    query = db.items.delete().where(db.items.c.owner_id == user_result["id"])
    conn.execute(query)

    query = db.users.delete().where(db.users.c.email == credentials["email"])
    conn.execute(query)
    proc.kill() 
