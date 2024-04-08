# -*- coding: utf-8 -*-
# @Time    : 2024/2/2 16:36
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : test_api.py
# @Software: PyCharm

from fastapi import FastAPI, HTTPException, Depends
from fastapi.routing import APIRoute
from fastapi.openapi.models import HTTPMethod

app = FastAPI()


class Item:
    def __init__(self, name: str, description: str = None):
        self.name = name
        self.description = description


class MethodView:
    async def dispatch(self, request, *args, **kwargs):
        method = request.method.lower()
        if hasattr(self, method):
            handler = getattr(self, method)
            return await handler(request, *args, **kwargs)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")


class ItemView(MethodView):
    async def get(self, request, item_id: int):
        return {"item_id": item_id}

    async def post(self, request, item: Item):
        return item


item_view = ItemView()


class MethodViewRoute(APIRoute):
    def get_route_handler(self):
        return item_view.dispatch


app.router.route_class = MethodViewRoute


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return await item_view.get(request, item_id)


@app.post("/items/")
async def create_item(item: Item):
    return await item_view.post(request, item)
