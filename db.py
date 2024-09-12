# -*- coding: utf-8 -*-
# @Time    : 2024/3/17 17:10
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : db.py.py
# @Software: PyCharm


from utils.db_connect import db_url as mysql_db_url
from utils.db_connect import pg_db_url as postgres_db_url
from utils.db_connect import models_list

TORTOISE_CONFIG = {
    "connections": {
        "default": mysql_db_url,
        # "default": postgres_db_url,
        # "mysql_db": mysql_db_url
    },
    "apps": {
        "models": {
            "models": models_list,
            "default_connection": "default",
        },
        # "postgres_models": {
        #     "models": models_list,
        #     "default_connection": "default",
        # },
        # "mysql_models": {
        #     "models": models_list,
        #     "default_connection": "mysql_db",
        # }
    },
    'use_tz': True,  # 确保 Tortoise 使用带时区的 datetime
    'timezone': 'Asia/Shanghai',
}

print(mysql_db_url)
"""
aerich init -t db.TORTOISE_CONFIG
aerich init-db

aerich --app mysql_models init-db

aerich migrate --name test
aerich upgrade
"""
