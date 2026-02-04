# -*- coding: utf-8 -*-
# @Time    : 2024/8/24 20:15
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : auth_api.py
# @Software: PyCharm

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.core.response import api_response
from app.core.security import get_token_header

router = APIRouter()


@router.get("", summary="用户详情")
async def user_info(admin=Depends(get_token_header)):
    """用户详情"""

    admin.pop("password", None)
    return api_response(data=jsonable_encoder(admin))
