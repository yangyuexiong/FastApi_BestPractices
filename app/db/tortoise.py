# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 15:33
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : db_connect.py
# @Software: PyCharm

import os
from typing import List

from loguru import logger
from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import get_config

project_config = get_config()
db_url = project_config.mysql_url
pg_db_url = project_config.pg_url

models_list: List[str] = [
    "aerich.models",
    "app.models.admin",
    "app.models.aps_task"
]

TORTOISE_CONFIG = {
    "connections": {
        "default": db_url,
    },
    "apps": {
        "models": {
            "models": models_list,  # 指定包含模型定义的模块
            "default_connection": "default",
        },
        # "models_db2": {
        #     "models": [],  # other_db 的模型模块
        #     "default_connection": "other_db",
        # },
    },
    "use_tz": True,
    "timezone": "Asia/Shanghai",
}


async def register_orm(app):
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


async def orm(app):
    """兼容旧调用入口"""
    await register_orm(app)


async def db_init():
    """数据库初始化"""

    await Tortoise.init(
        db_url=db_url,
        modules={
            "models": models_list
        }
    )
    logger.info(f'Mysql初始化:{db_url}')


async def db_init_pg():
    """数据库初始化"""

    await Tortoise.init(
        db_url=pg_db_url,
        modules={
            "models": models_list
        }
    )

    logger.info(f'Postgresql初始化:{pg_db_url}')


async def db_init_debug():
    """数据库初始化(调试)"""

    logger.debug(db_url)

    await Tortoise.init(
        db_url=db_url,
        modules={
            "models": models_list
        }
    )

    logger.info('>>> Mysql初始化')

    # 迁移模式
    await Tortoise.generate_schemas()


if __name__ == '__main__':
    # run_async(db_init_debug())

    logger.info(f"TORTOISE_CONFIG:{TORTOISE_CONFIG}")  # aerich init -t your_app.tortoise_conf.TORTOISE_CONFIG

    PROJECT_NAME = os.path.dirname(os.path.abspath(__file__)).split('/')[-1]
    current_file_name = os.path.basename(__file__).split('.py')[0]
    command = f"aerich init -t {PROJECT_NAME}.{current_file_name}.TORTOISE_CONFIG"
    logger.info(command)

    """
    初始化:
        aerich init -t app.db.tortoise.TORTOISE_CONFIG
        aerich init-db
        
    迁移:
        aerich migrate
        aerich upgrade
    """
