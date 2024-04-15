# -*- coding: utf-8 -*-
# @Time    : 2024/4/14 19:01
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : common_page.py
# @Software: PyCharm


from pydantic import BaseModel


class CommonPage(BaseModel):
    page: int = 1
    size: int = 20


async def page_size(page: int, size: int) -> tuple:
    return (page - 1) * size, size
