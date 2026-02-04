# -*- coding: utf-8 -*-
# @Time    : 2026/2/3
# @Author  : yangyuexiong
# @File    : router.py

from fastapi import APIRouter

from app.api.v1.routers.admin import router as admin_router
from app.api.v1.routers.admin_login import router as admin_login_router
from app.api.v1.routers.auth import router as auth_router

api_router = APIRouter(prefix="/api", responses={404: {"description": "Not found"}})

api_router.include_router(auth_router, prefix="/auth", tags=["鉴权"])
api_router.include_router(admin_router, prefix="/admin", tags=["用户管理"])
api_router.include_router(admin_login_router, prefix="/account", tags=["账户"])
