# -*- coding: utf-8 -*-
# @Time    : 2023/12/29 18:13
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : login_api.py
# @Software: PyCharm

from datetime import datetime
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
user_router = APIRouter()
item_router = APIRouter()

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


class AdminCreate(BaseModel):
    username: str
    password: str


class AdminResponse(BaseModel):
    id: int
    username: str
    remark: Union[str, None] = None
    create_time: datetime


# @login_router.post("/create", response_model=Admin_Pydantic)
@login_router.post("/create", response_model=AdminResponse)
async def login_test(admin_data: AdminCreate):
    # 直接创建
    # admin_obj = await Admin.create(
    #     username=admin_data.username,
    #     password=admin_data
    # )

    # 创建 Admin 对象
    admin_obj = Admin(username=admin_data.username)

    # 使用 set_password 方法对密码进行加密
    await admin_obj.set_password(admin_data.password)

    # 保存到数据库
    await admin_obj.save()

    # 返回创建的 admin 对象
    print(admin_obj)
    return admin_obj


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


class CommonQueryParams:
    def __init__(self, q: Union[str, None] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@user_router.get("/user_list/")
async def user_list(commons: CommonQueryParams = Depends()):
    """用户列表"""

    # print(get_settings().app_name)
    return commons


@user_router.get("/{user_id}", response_model=Admin_Pydantic)
async def user(user_id: int):
    """用户详情"""

    user = await Admin.get(id=user_id)
    print(user, type(user))
    user2 = await Admin_Pydantic.from_queryset_single(Admin.get(id=user_id))
    print(user2, type(user2))

    if user:
        return user2
    return {}


def validate_query_param(q: Union[str, None] = Query(default=None, max_length=2)):
    try:
        if len(q) > 2:
            raise ValueError("String should have at most 2 characters")
        return q
    except ValueError as ve:
        # 在验证失败时抛出自定义的HTTPException
        raise HTTPException(status_code=422, detail={"error": "Custom validation error", "message": str(ve)})


@item_router.get("/")
async def read_items(q: Annotated[Union[str, None], Cookie()]):
    # async def read_items(q: Union[str, None] = Query(default=None, max_length=2)):
    """数据列表"""

    query_items = {"q": q}
    # raise HTTPException(status_code=404, detail="Resource not found")
    return query_items
