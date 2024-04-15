# -*- coding: utf-8 -*-
# @Time    : 2023/12/29 18:13
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : login_api.py
# @Software: PyCharm

from typing import Union, List, Annotated

from fastapi import APIRouter, Depends, Header, Query, Cookie, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from common.libs.custom_exception import CustomException
from common.libs.api_result import api_result
from app.models.admin.models import Admin, Admin_Pydantic
import utils.redis_connect as rp
from utils.redis_connect import get_value, set_key_value

login_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class LoginReqBody(BaseModel):
    """登录请求体参数与类型"""

    username: str
    password: str
    title: str = "okc"
    login_type: Union[str, int, None] = None


class LoginOut(BaseModel):
    """响应模型"""

    username: str
    title: str
    age: int = 666
    login_type: Union[str, int, None] = None
    tags: list = []


class Message(BaseModel):
    message: str


"""
response_model_exclude_unset:
    只返回`response_model`中有值的字段:   response_model_exclude_unset=True

response_model_include:
    只返回`response_model`中需要的字段:   {"username", "title", ...}

response_model_exclude:
    去掉`response_model`中不需要的字段:   {"username", "title", ...}
    
"""


async def verify_token(x_token: str = Header()):
    if x_token != "yyx":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header()):
    if x_key != "123":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


"""
局部拦截器:
    dependencies=[Depends(verify_token), Depends(verify_key)]

"""


@login_router.post(
    "/",
    response_model=LoginOut,
    dependencies=[Depends(verify_token), Depends(verify_key)],
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": Message, "description": "The item was not found"},
        200: {
            "description": "Item requested by ID",
            "content": {
                "application/json": {
                    "example": {"id": "bar", "value": "The bar tenders"}
                }
            },
        },
    },
)
# @login_router.post("/", response_model=LoginOut, response_model_exclude_unset=True)
# @login_router.post("/", response_model=LoginOut, response_model_include={"username", "title"})
# @login_router.post("/", response_model=LoginOut, response_model_exclude={"username", "title"})
async def login(data: LoginReqBody):
    """登录"""

    print(">>> redis_pool id", rp.redis_pool, type(rp.redis_pool), id(rp.redis_pool))
    val = await rp.redis_pool.get("0.0.0.0")
    print('>>> val', val, type(val), id(val))
    val2 = await get_value("0.0.0.0")
    print('>>> val2', val, type(val2), id(val2))

    await set_key_value("ok2024_123", "hhh")

    print(data.username)
    print(data.password)
    print(data)
    print(jsonable_encoder(data))
    # print(1 / 0)
    # raise CustomException(status_code=400, detail="自定义异常", custom_code=100001, data=[1, 2, 3])
    # return data
    # print(get_settings().app_name)
    headers = {
        "X-Cat-Dog": "alone in the world",
        "Content-Language": "en-US"
    }
    content = api_result(code=status.HTTP_200_OK, message="登录成功", data=jsonable_encoder(data))
    response = JSONResponse(status_code=status.HTTP_200_OK, content=content, headers=headers)
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response
