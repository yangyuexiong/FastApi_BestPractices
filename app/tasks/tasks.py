# -*- coding: utf-8 -*-
# @Time    : 2024/8/26 13:47
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : tasks.py
# @Software: PyCharm


from app.core.config import get_config

project_config = get_config()


async def test_async_task(*args, **kwargs):
    import os
    os.environ['yyx'] = 'okc'
    print(f"test_async_task: {os.getenv('yyx')}", args, kwargs)


def test_sync_task(*args, **kwargs):
    import os
    print(f"test_sync_task: {os.getenv('yyx')}", args, kwargs)
