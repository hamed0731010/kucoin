import asyncio
from typing import Union

from starlette.websockets import WebSocketDisconnect

from new_redis import rate_list,redis_client
from fastapi import Response,FastAPI,WebSocket
from pydantic import BaseModel
from fastapi.params import Depends
import  uvicorn
import  requests
import  httpx
import threading
import redis
from fastapi.responses import HTMLResponse
import json
async def fetch_store():
    base_url = 'https://api.kucoin.com'
    path = '/api/v1/market/allTickers'
    async with httpx.AsyncClient() as client:
        response = await client.get(base_url + path)
        data = response.json()
        json_str = json.dumps(data)
        redis_client.set('person:1', json_str)

app = FastAPI()
health_status = fetch_store()
list_rate = rate_list()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.websocket("/")
async def read_status(websocket:WebSocket):
    await  websocket.accept()
    while True:
        data=redis_client.get('foo')
        if data:
            await  websocket.send_text(data)
            #healthstatus=websocket.receive_json()
        try:
            message = await websocket.receive_text()
            print(f"Received message: {message}")
            # Process the received message or perform other actions
        except WebSocketDisconnect:
            # Handle WebSocket disconnection
            break

@app.on_event('startup')
async  def startup_event():
    await fetch_store()
    async  def update_date():
        while True:
            await fetch_store()
            await  asyncio.sleep(10)
    asyncio.create_task(update_date())
@app.get("/list/")
async def read_list():

    ratelist = redis_client.get('foo')

    return ratelist

@app.get('/')
async  def show_api(response: Response):
        result=redis_client.get('person:1')
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return  result
async def common_parameters(
        q: Union[str, None] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.price, "item_id": item_id}

@app.get("/url-list")
def get_all_urls():
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    return url_list

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)