# -*- coding: utf-8 -*-
# @Time    : 2024/4/17 15:57
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : demo_api.py
# @Software: PyCharm


from all_reference import *


async def get_token_header(x_token: str = Header(), token: str = Header(), a_123: str = Header()):
    print(f"x_token:{x_token}")
    print(f"token:{token}")
    print(f"a_123:{a_123}")
    if x_token != "fake-super-secret-token":
        raise CustomException(404, "xxx", 10002, {"key": "value"})


demo_router = APIRouter(
    dependencies=[Depends(get_token_header)]
)


@demo_router.get("/demo")
async def demo():
    return {
        "code": 200,
        "message": "demo api"
    }
