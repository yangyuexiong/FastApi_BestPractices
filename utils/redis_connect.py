# -*- coding: utf-8 -*-
# @Time    : 2024/4/5 17:33
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : redis_connect.py
# @Software: PyCharm


import aioredis
from aioredis import Redis

from config.config import get_config

project_config = get_config()

REDIS_PWD = project_config.REDIS_PWD
REDIS_HOST = project_config.REDIS_HOST
REDIS_PORT = project_config.REDIS_PORT
REDIS_DB = project_config.REDIS_DB
DECODE_RESPONSES = project_config.DECODE_RESPONSES
REDIS_URL = f"redis://:{REDIS_PWD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}?decode_responses={DECODE_RESPONSES}"

"""
全局变量用于存储 Redis 连接池
整个应用程序生命周期中共享同一个 Redis 连接池，同时不会出现循环引用。

正确引用方式:
    import utils.redis_connect as rp
    rp.redis_pool.get("key")

错误引用方式:
    from utils.redis_connect import redis_pool
    redis_pool.get("key")

这种导入方式只会获取 redis_pool 变量的初始值，而不会动态更新它的值。
因此，即使在应用启动时已经调用了 create_redis_connection_pool() 函数来创建了 Redis 连接池，
并且 redis_pool 已经被赋值为正确的连接池对象，但是上述引用方式 redis_pool 仍然是最初的 None 值。

"""
redis_pool: Redis = None


async def create_redis_connection_pool():
    """在应用启动时创建连接池"""
    global redis_pool
    redis_pool = await aioredis.from_url(REDIS_URL)


async def close_redis_connection_pool():
    """在应用关闭时关闭连接池"""
    if redis_pool:
        await redis_pool.close()


async def set_key_value(key, value, ex=None):
    """设置键值对"""
    await redis_pool.set(key, value, ex)


async def get_value(key):
    """获取键的值"""
    value = await redis_pool.get(key)
    return value


async def delete_value(key):
    """删除"""
    await redis_pool.delete(key)
