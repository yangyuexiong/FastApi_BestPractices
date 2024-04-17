# -*- coding: utf-8 -*-
# @Time    : 2023/12/29 18:07
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : __init__.py.py
# @Software: PyCharm


from fastapi import APIRouter, Depends

from app.api.demo_api.demo_api import demo_router
from app.api.test_exception_api.test_exception_api import test_exception_router
from app.api.login_api.login_api import login_router
from app.api.admin_api.admin_api import admin_router
from app.api.admin_api.login_api import admin_login_router

api = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={
        404: {"description": "Not found"}
    },
)

# 将子路由添加到主路由
api.include_router(demo_router, prefix="/demo_test", tags=["例子"])
api.include_router(test_exception_router, prefix="/exp_test", tags=["异常测试"])
api.include_router(admin_router, prefix="/admin", tags=["管理员"])
api.include_router(admin_login_router, prefix="/admin", tags=["管理员登录"])
api.include_router(login_router, prefix="/login", tags=["登录"])
# api.include_router(user_router, prefix="/user", tags=["用户"])
