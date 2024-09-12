# -*- coding: utf-8 -*-
# @Time    : 2024/8/26 13:47
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : tasks.py
# @Software: PyCharm


from config.config import get_config

project_config = get_config()


async def test_task(*args, **kwargs):
    print('test_task', args, kwargs)
