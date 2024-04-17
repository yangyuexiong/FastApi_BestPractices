# -*- coding: utf-8 -*-
# @Time    : 2024/4/17 23:46
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : login_api.py
# @Software: PyCharm

import json

from all_reference import *
from app.models.admin.models import Admin, Admin_Pydantic
from common.libs.auth import Token

admin_login_router = APIRouter()


class AdminLogin(BaseModel):
    username: str = "admin"
    password: str = "123456"


@admin_login_router.post("/login")
async def admin_login(request_data: AdminLogin):
    """admin登录"""

    username = request_data.username
    password = request_data.password

    admin = await Admin.filter(username=username).first()

    if not admin:
        content = api_result(code=10002, message=f"管理员用户 {username} 不存在")
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)

    verify_result = await admin.verify_password(password)
    if not verify_result:
        content = api_result(code=10005, message="密码错误")
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)
    else:
        admin_result = await Admin_Pydantic.from_tortoise_orm(admin)

        admin_key_prefix = f"tk_{admin.id}_{admin.username}_"
        user_info_str = json.dumps(jsonable_encoder(admin_result))

        new_auth = Token()

        if admin.login_type == "single":  # 单点登录
            await new_auth.single_login(key=admin_key_prefix, user_info_json_str=user_info_str)
        else:
            await new_auth.many_login(key=admin_key_prefix, user_info_json_str=user_info_str)

        result = jsonable_encoder(admin_result)
        result["token"] = new_auth.token
        content = api_result(code=status.HTTP_200_OK, message="登录成功", data=result)
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@admin_login_router.get("/user_info/{token}")
async def get_user_info(token: str):
    """获取用户信息"""

    user_info = await Token.get_user_info(token)
    if user_info:
        code = status.HTTP_200_OK
        content = api_result(code=code, data=user_info)
    else:
        code = status.HTTP_401_UNAUTHORIZED
        content = api_result(code=code, data=user_info)
    return JSONResponse(status_code=code, content=content)
