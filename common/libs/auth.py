# -*- coding: utf-8 -*-
# @Time    : 2024/4/18 00:25
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : auth.py
# @Software: PyCharm

import uuid
import json

import utils.redis_connect as rp
from utils.redis_connect import get_value, set_key_value


class Token:
    """
    Token
    """

    def __init__(self):
        self.token = None
        self.mix = "Y"
        self.timeout = 3600 * 24 * 30

    async def gen_token(self):
        """
        生成token
        :return:
        """

        token = str(uuid.uuid1()).replace('-', self.mix)
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
        print(old_key_list)
        print(old_token_list)
        await rp.redis_pool.delete(*old_key_list)
        await rp.redis_pool.delete(*old_token_list)

        await self.gen_token()
        await set_key_value(f"{key}{self.token}", self.token, self.timeout)  # 设置新token
        await set_key_value(self.token, user_info_json_str, self.timeout)  # 设置用户信息

    async def many_login(self, key: str, user_info_json_str: str):
        """多点登录"""

        await self.gen_token()
        await set_key_value(f"{key}{self.token}", self.token, self.timeout)  # 设置新token
        await set_key_value(self.token, user_info_json_str, self.timeout)  # 设置用户信息