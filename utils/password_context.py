# -*- coding: utf-8 -*-
# @Time    : 2024/4/14 16:27
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : password_context.py
# @Software: PyCharm

import bcrypt


def hash_password(password: str) -> str:
    """加密密码"""

    # 生成盐
    salt = bcrypt.gensalt()
    # 使用盐加密密码
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


if __name__ == '__main__':
    # 示例用法
    raw_password = "password123"
    hashed_password = hash_password(raw_password)
    print(f"Hashed Password: {hashed_password}")

    # 验证密码
    is_valid = verify_password(raw_password, hashed_password)
    print(f"Password is valid: {is_valid}")

    # 测试错误的密码
    is_valid = verify_password("wrongpassword", hashed_password)
    print(f"Password is valid: {is_valid}")
