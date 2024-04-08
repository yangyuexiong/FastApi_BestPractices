# -*- coding: utf-8 -*-
# @Time    : 2024/2/5 17:49
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : custom_exception.py
# @Software: PyCharm

from fastapi import HTTPException


# 自定义异常
class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str, custom_code: int, data: any = None):
        super().__init__(status_code=status_code, detail=detail)
        self.custom_code = custom_code
        self.data = data
