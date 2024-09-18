# -*- coding: utf-8 -*-
# @Time    : 2024/7/26 18:36
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : admin_login_api.py
# @Software: PyCharm

import json

from all_reference import *
from app.models.admin.models import Admin
from common.libs.auth import Token

admin_login_router = APIRouter()


class AdminLogin(BaseModel):
    username: str
    password: str


@admin_login_router.post("/login")
async def admin_login(request_data: AdminLogin):
    """admin登录"""

    username = request_data.username
    password = request_data.password

    admin = await Admin.filter(username=username).first()

    if not admin:
        return api_response(code=10002, message=f"管理员用户 {username} 不存在")

    if admin.status == 99:
        return api_response(code=10002, message=f"用户 {admin.username} 已禁用")

    verify_result = await admin.verify_password(password)
    if not verify_result:
        return api_response(code=10005, message="密码错误")
    else:

        admin_key_prefix = f"tk_{admin.id}_{admin.username}_"
        user_info_str = json.dumps(jsonable_encoder(admin))

        new_auth = Token()

        if admin.login_type == "single":  # 单点登录
            await new_auth.single_login(key=admin_key_prefix, user_info_json_str=user_info_str)
        else:
            await new_auth.many_login(key=admin_key_prefix, user_info_json_str=user_info_str)

        result = jsonable_encoder(admin, exclude={"password"})
        result["token"] = new_auth.token
        return api_response(message="登录成功", data=result)


@admin_login_router.delete("/logout")
async def admin_logout(token: str = Header()):
    """admin退出"""

    await delete_value(token)
    return api_response(message=f"操作成功:{token}")
