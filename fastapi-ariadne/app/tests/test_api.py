import pytest
import time
import httpx
import json
import asyncio
from websockets import connect
from ariadne.asgi import (
    GQL_CONNECTION_INIT,
    GQL_CONNECTION_ACK,
    GQL_START,
    GQL_DATA,
    GQL_STOP,
    GQL_COMPLETE,
    GQL_CONNECTION_TERMINATE,
)
from threading import Timer

my_storage = {}

@pytest.fixture
def storage():
    return my_storage


@pytest.mark.asyncio
async def test_create_user(server, host, credentials, storage):
    query = '''
        mutation createUser($email: String!, $password: String!) {
            createUser(email: $email, password: $password) {
                id,
                errors
            }
        }
    '''

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'http://{host}/',
            timeout=60,
            json = { 
            "query": query,
            "variables": credentials
            })
        json_response = json.loads(response.text)
        assert ('errors' in json_response) == False
        assert json_response["data"]["createUser"]['id'] is not None
        storage["user_id"] = json_response["data"]["createUser"]['id']

@pytest.mark.asyncio
async def test_auth_user(server, host, credentials, storage):
    query = '''
    mutation authUser($email: String!, $password: String!) {
        createToken(email: $email, password: $password) {
		    errors,
            token
        }
    }
    '''

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'http://{host}/',
            headers={},
            timeout=60,
            json = { 
            "query": query,
            "variables": credentials
            })
        json_response = json.loads(response.text)
        assert ('errors' in json_response) == False
        assert (json_response["data"]["createToken"]["token"] is not None)
        storage["token"] = json_response["data"]["createToken"]["token"] 


async def create_item(server, host, storage):
    query = '''
    mutation createItem($title: String!, $description: String!) {
        createItem(title: $title, description: $description) {
		    errors
            id
        }
    }
    '''
    token = storage["token"]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'http://{host}/',
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
            json = { 
            "query": query,
            "variables": {'title': 'title', 'description': 'description'},
            })
        json_response = json.loads(response.text)
        assert ('errors' in json_response) == False
        assert (json_response["data"]['createItem']['id'] is not None)


@pytest.mark.asyncio
async def test_create_item(server, host, storage):
    await create_item(server, host, storage)


@pytest.mark.asyncio
async def test_subscription(server, host, storage):
    query = """
        subscription getItemUpdates($token: String!) {
            new_item(token: $token) {
                errors
                id
            }
        }
    """
    variables = {"token": f'Bearer {storage["token"]}'}
    ws = await connect(f'ws://{host}/', subprotocols='graphql-ws')
    await ws.send(json.dumps({"type": GQL_CONNECTION_INIT}))
    await ws.send(
            json.dumps({
                "type": GQL_START,
                "payload": {"query": query, "variables": variables},
            })
        )
    received = await ws.recv()
    assert received == '{"type": "connection_ack"}'

    def delay_create_item(server, host, storage):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(create_item(server, host, storage))

    timer = Timer(1.0, delay_create_item, (server, host, storage))
    timer.start()

    received = await ws.recv()
    await ws.close()
    json_response = json.loads(received)
    assert ('errors' in json_response) == False
    assert json_response["payload"]['data']['new_item']['id'] is not None
