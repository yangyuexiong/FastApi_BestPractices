# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 15:33
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : redis_client.py
# @Software: PyCharm


from typing import Optional

from loguru import logger
from redis.asyncio import Redis

from app.core.config import get_config

project_config = get_config()
REDIS_URL = project_config.redis_url

"""
全局变量用于存储 Redis 连接池
整个应用程序生命周期中共享同一个 Redis 连接池，同时不会出现循环引用。

正确引用方式:
    import app.db.redis_client as rp
    rp.redis_pool.get("key")

错误引用方式:
    from app.db.redis_client import redis_pool
    redis_pool.get("key")

这种导入方式只会获取 redis_pool 变量的初始值，而不会动态更新它的值。
因此，即使在应用启动时已经调用了 create_redis_connection_pool() 函数来创建了 Redis 连接池，
并且 redis_pool 已经被赋值为正确的连接池对象，但是上述引用方式 redis_pool 仍然是最初的 None 值。

"""
redis_pool: Optional[Redis] = None


async def create_redis_connection_pool(force: bool = False) -> Redis:
    """在应用启动时创建连接池"""
    global redis_pool
    if redis_pool and not force:
        return redis_pool
    if redis_pool and force:
        await close_redis_connection_pool()
    redis_pool = Redis.from_url(REDIS_URL)
    logger.info("Redis 连接池已创建")
    return redis_pool


async def close_redis_connection_pool():
    """在应用关闭时关闭连接池"""
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        redis_pool = None
        logger.info("Redis 连接池已关闭")


async def get_redis_pool() -> Redis:
    """获取连接池，未初始化时抛出异常"""
    if not redis_pool:
        raise RuntimeError("Redis 连接池未初始化，请先调用 create_redis_connection_pool()")
    return redis_pool


async def set_key_value(key, value, ex=None):
    """设置键值对"""
    pool = await get_redis_pool()
    await pool.set(key, value, ex)


async def get_value(key):
    """获取键的值"""
    pool = await get_redis_pool()
    value = await pool.get(key)
    return value


async def delete_value(key):
    """删除"""
    pool = await get_redis_pool()
    await pool.delete(key)


async def redis_one_get(k):
    """单点连接"""

    redis = Redis.from_url(REDIS_URL)
    res = await redis.get(k)
    await redis.close()
    return res


async def redis_one_set(k, v):
    """单点连接"""

    redis = Redis.from_url(REDIS_URL)
    await redis.set(k, v)
    await redis.close()
