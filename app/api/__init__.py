# -*- coding: utf-8 -*-
# @Time    : 2023/12/29 18:07
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : __init__.py.py
# @Software: PyCharm


from fastapi import APIRouter, Depends

from app.api.login_api.login_api import login_router, user_router, item_router
from app.api.admin_api.admin_api import admin_router

api = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

# 将子路由添加到主路由
api.include_router(admin_router, prefix="/admin", tags=["管理员"])
api.include_router(login_router, prefix="/login", tags=["登录"])
api.include_router(user_router, prefix="/user", tags=["用户"])
api.include_router(item_router, prefix="/item_list", tags=["数据列表"])
