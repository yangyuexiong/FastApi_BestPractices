# -*- coding: utf-8 -*-
# @Time    : 2024/3/17 17:10
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : db.py.py
# @Software: PyCharm


from config.config import get_config
from utils.db_connect import models_list

project_config = get_config()

db_url = "mysql://{}:{}@{}:{}/{}".format(
    project_config.MYSQL_USERNAME,
    project_config.MYSQL_PASSWORD,
    project_config.MYSQL_HOSTNAME,
    project_config.MYSQL_PORT,
    project_config.MYSQL_DATABASE
)
print(db_url)

TORTOISE_CONFIG = {
    "connections": {
        "default": db_url,
    },
    "apps": {
        "models": {
            "models": models_list,
            "default_connection": "default",
        }
    },
}

"""
aerich init -t db.TORTOISE_CONFIG
aerich init-db


aerich migrate --name test
aerich upgrade
"""
