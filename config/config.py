# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 15:34
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : config.py
# @Software: PyCharm

import os

from functools import lru_cache

from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """配置基类"""

    # 基础配置
    APP_NAME: str = "yangyuexiong"
    ENV: str
    SECRET_KEY: str
    DEBUG: bool
    RUN_HOST: str
    RUN_PORT: int

    # MySQL配置
    MYSQL_HOSTNAME: str
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str
    MYSQL_PORT: int
    MYSQL_DATABASE: str

    # POSTGRESQL配置
    POSTGRESQL_HOSTNAME: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_PORT: int
    POSTGRESQL_DATABASE: str

    # Redis配置
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PWD: str
    REDIS_DB: int
    DECODE_RESPONSES: bool


class DevelopmentConfig(BaseConfig):
    """Dev配置"""

    class Config:
        env_file = f"{os.path.dirname(os.path.abspath(__file__))}/dev.ini"


class ProductionConfig(BaseConfig):
    """Prod配置"""

    class Config:
        env_file = f"{os.path.dirname(os.path.abspath(__file__))}/pro.ini"


@lru_cache
def get_config():
    """获取配置文件"""

    fast_api_env = os.getenv("FAST_API_ENV")
    print(f'>>> fast_api_env: {fast_api_env}')
    if fast_api_env == 'development':
        conf = DevelopmentConfig()
    else:
        conf = ProductionConfig()
    return conf


if __name__ == '__main__':
    dev_config = DevelopmentConfig()
    print(dev_config.dict())
    print(dev_config.APP_NAME)
    print(dev_config.MYSQL_HOSTNAME)

    pro_config = ProductionConfig()
    print(pro_config.dict())
