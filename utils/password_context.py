# -*- coding: utf-8 -*-
# @Time    : 2024/4/14 16:27
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : password_context.py
# @Software: PyCharm


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
