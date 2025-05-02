# -*- coding: utf-8 -*-
# @Time    : 2024/8/24 20:15
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : auth_api.py
# @Software: PyCharm

from all_reference import *

auth_router = APIRouter()


@auth_router.get("", summary="用户详情")
async def user_info(admin=Depends(get_token_header)):
    """用户详情"""

    del admin["password"]
    return api_response(data=jsonable_encoder(admin))
