# -*- coding: utf-8 -*-
# @Time    : 2024/4/18 00:25
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : auth.py
# @Software: PyCharm

import json
import secrets

from fastapi import Depends, Header
from loguru import logger

import app.db.redis_client as rp
from app.core.exceptions import CustomException
from app.db.redis_client import get_value, set_key_value
from app.models.admin import Admin


class Token:
    """
    Token
    """

    def __init__(self):
        self.token = None
        self.timeout = 3600 * 24 * 30

    async def gen_token(self):
        """
        生成token
        :return:
        """

        token = secrets.token_urlsafe(32)
        self.token = token
        return token

    @staticmethod
    async def get_user_info(token: str):
        """
        通过token或用户信息
        :param token:
        :return:
        """

        query_user_info = await get_value(token)
        if not query_user_info:
            return False
        else:
            user_info = json.loads(query_user_info)
            return user_info

    async def single_login(self, key: str, user_info_json_str: str):
        """单点登录"""

        # 获取该用户所有有效的key和token并且删除
        old_key_list = await rp.redis_pool.keys(pattern=f"{key}*")
        old_token_list = [await get_value(old_key) for old_key in old_key_list]
        if old_key_list or old_token_list:
            logger.debug(f"single_login revoke tokens: keys={len(old_key_list)} tokens={len(old_token_list)}")
        if old_key_list:
            await rp.redis_pool.delete(*old_key_list)
        if old_token_list:
            await rp.redis_pool.delete(*old_token_list)

        await self.gen_token()
        await set_key_value(f"{key}{self.token}", self.token, self.timeout)  # 设置新token
        await set_key_value(self.token, user_info_json_str, self.timeout)  # 设置用户信息

    async def many_login(self, key: str, user_info_json_str: str):
        """多点登录"""

        await self.gen_token()
        await set_key_value(f"{key}{self.token}", self.token, self.timeout)  # 设置新token
        await set_key_value(self.token, user_info_json_str, self.timeout)  # 设置用户信息


async def get_token_header(token: str = Header()):
    """校验token"""

    query_user_info = await get_value(token)
    if not query_user_info:
        raise CustomException(detail="未授权", custom_code=401)
    else:
        user_info = json.loads(query_user_info)
        return user_info


async def check_admin_existence(user_info: dict = Depends(get_token_header)):
    """检查后台用户是否存在"""

    admin_id = user_info.get("id")
    admin = await Admin.get_or_none(id=admin_id)
    if not admin:
        raise CustomException(detail=f"后台用户 {admin_id} 不存在", custom_code=10002)
    return admin
