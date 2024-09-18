# -*- coding: utf-8 -*-
# @Time    : 2024/8/23 14:02
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : __init__.py.py
# @Software: PyCharm

from fastapi import APIRouter

from app.api.auth_api.auth_api import auth_router
from app.api.admin_api.admin_api import admin_router
from app.api.admin_api.admin_login_api import admin_login_router

# 一级路由
api = APIRouter(prefix="/api", tags=["api"], responses={404: {"description": "Not found"}})

# 二级路由
admin = APIRouter(prefix="/admin", tags=["后台"])

# 三级路由-后台
admin.include_router(auth_router, prefix="/auth", tags=["鉴权"])
admin.include_router(admin_router, tags=["用户管理"])
admin.include_router(admin_login_router, prefix="/account", tags=["账户"])

# 统一注册
api.include_router(admin)
