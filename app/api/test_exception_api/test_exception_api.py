# -*- coding: utf-8 -*-
# @Time    : 2024/4/17 16:23
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : test_exception_api.py
# @Software: PyCharm


from all_reference import *

test_exception_router = APIRouter()


@test_exception_router.get("/base_exception")
async def test_base_exception():
    print(1 / 0)
    return {
        "code": 200,
        "message": "test_exception api"
    }
