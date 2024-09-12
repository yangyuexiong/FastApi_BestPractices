# -*- coding: utf-8 -*-
# @Time    : 2024/5/7 19:30
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : common_enum.py
# @Software: PyCharm


from enum import Enum


class UserStatus(str, Enum):
    normal = '正常'
    disable = '禁用'
