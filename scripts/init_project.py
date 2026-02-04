# -*- coding: utf-8 -*-
# @Time    : 2024/5/14 18:15
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : project_init.py
# @Software: PyCharm

import os
import shutil
import sys

import pytz
import subprocess
from datetime import datetime

from tortoise import run_async

from app.core.password import hash_password
from app.db.tortoise import db_init as mysql_db_init
from app.models.admin import Admin


class ProjectInit:
    """项目初始化"""

    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    now_str = now.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')
    now_timestamp = int(now.timestamp())
    time_dict = {
        "create_time": now,
        "update_time": now,
        "update_timestamp": now_timestamp
    }
    create_dict = {
        "creator": "init",
        "creator_id": 0,
        "remark": "脚本初始化",
    }

    @classmethod
    def db_init(cls):
        """
        初始化数据库表
        aerich init -t app.db.tortoise.TORTOISE_CONFIG
        aerich init-db
        """

        # 检查当前目录是否存在 migrations 文件夹，如果存在，删除 migrations 文件夹及其内容
        if os.path.exists("migrations"):
            shutil.rmtree("migrations")
            print("已删除 migrations 文件夹")

        # aerich init -t app.db.tortoise.TORTOISE_CONFIG
        result_init = subprocess.run(['aerich', 'init', '-t', 'app.db.tortoise.TORTOISE_CONFIG'],
                                     capture_output=True, text=True)
        print("aerich init 输出：", result_init.stdout)

        # aerich init-db
        result_init_db = subprocess.run(['aerich', 'init-db'], capture_output=True, text=True)
        print("aerich init-db 输出：", result_init_db.stdout)

    @classmethod
    async def create_admin(cls):
        """后台管理员账号"""

        admin_list = [
            {
                "username": "admin",
                "password": "123456",
                "nickname": "管理员-admin",
                "remark": "ProjectInit",
                **cls.time_dict
            },
            {
                "username": "super",
                "password": "123456",
                "nickname": "管理员-super",
                "remark": "ProjectInit",
                **cls.time_dict
            },
            {
                "username": "yyx",
                "password": "123456",
                "nickname": "管理员-yyx",
                "remark": "ProjectInit",
                **cls.time_dict
            }
        ]

        await mysql_db_init()

        for admin in admin_list:
            username = admin.get("username")
            password = admin.get("password")
            q_admin = await Admin.filter(username=username).first()
            if q_admin:
                print(f"账号: {username} 已存在")
            else:
                # 加密密码
                # hashed_password = pwd_context.hash(password)
                hashed_password = hash_password(password)
                admin["password"] = hashed_password

                # 创建新的管理员账号
                await Admin.create(**admin)
                print(f"账号: {username} 新增成功")


if __name__ == '__main__':
    pi = ProjectInit()
    pi.db_init()
    run_async(pi.create_admin())
