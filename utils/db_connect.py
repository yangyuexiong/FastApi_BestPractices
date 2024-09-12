# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 15:33
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : db_connect.py
# @Software: PyCharm

import os

from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise

from config.config import get_config

project_config = get_config()

db_url = "mysql://{}:{}@{}:{}/{}".format(
    project_config.MYSQL_USERNAME,
    project_config.MYSQL_PASSWORD,
    project_config.MYSQL_HOSTNAME,
    project_config.MYSQL_PORT,
    project_config.MYSQL_DATABASE
)

pg_db_url = "postgres://{}:{}@{}:{}/{}".format(
    project_config.POSTGRESQL_USERNAME,
    project_config.POSTGRESQL_PASSWORD,
    project_config.POSTGRESQL_HOSTNAME,
    project_config.POSTGRESQL_PORT,
    project_config.POSTGRESQL_DATABASE
)

models_list = [
    "aerich.models",
    "app.models.admin.models"
]

TORTOISE_CONFIG = {
    "connections": {
        "default": db_url,
    },
    "apps": {
        "models": {
            "models": models_list,  # 指定包含模型定义的模块
            "default_connection": "default",
        }
    },
}


async def orm(app):
    """数据库迁移"""

    register_tortoise(
        app,
        db_url=db_url,
        modules={
            "models": models_list
        },
        generate_schemas=True,
        add_exception_handlers=True,
    )


async def db_init():
    """数据库初始化"""

    await Tortoise.init(
        db_url=db_url,
        modules={
            "models": models_list
        }
    )

    print(f'Mysql初始化:{db_url}')


async def db_init_pg():
    """数据库初始化"""

    await Tortoise.init(
        db_url=pg_db_url,
        modules={
            "models": models_list
        }
    )

    print(f'Postgresql初始化:{pg_db_url}')


async def db_init_debug():
    """数据库初始化(调试)"""

    print(db_url)

    await Tortoise.init(
        db_url=db_url,
        modules={
            "models": models_list
        }
    )

    print(f'>>> Mysql初始化')

    # 迁移模式
    await Tortoise.generate_schemas()


if __name__ == '__main__':
    # run_async(db_init_debug())

    print(f"TORTOISE_CONFIG:{TORTOISE_CONFIG}")  # aerich init -t your_app.tortoise_conf.TORTOISE_CONFIG

    PROJECT_NAME = os.path.dirname(os.path.abspath(__file__)).split('/')[-1]
    current_file_name = os.path.basename(__file__).split('.py')[0]
    command = f"aerich init -t {PROJECT_NAME}.{current_file_name}.TORTOISE_CONFIG"
    print(command)

    """
    初始化:
        aerich init -t utils.db_connect.TORTOISE_CONFIG
        aerich init-db
        
    迁移:
        aerich migrate
        aerich upgrade
    """
