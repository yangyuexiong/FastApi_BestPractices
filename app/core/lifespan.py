# -*- coding: utf-8 -*-
# @Time    : 2026/2/4
# @Author  : yangyuexiong
# @File    : lifespan.py

import datetime
import os
import platform
import threading
from contextlib import asynccontextmanager, suppress

from apscheduler.schedulers.base import SchedulerNotRunningError
from fastapi import FastAPI
from loguru import logger
from tortoise import Tortoise

import app.db.redis_client as redis_module
from app.core.config import get_config
from app.db.redis_client import close_redis_connection_pool, create_redis_connection_pool
from app.db.tortoise import TORTOISE_CONFIG
from app.tasks.scheduler import scheduler, scheduler_init

project_config = get_config()


def _log_startup_info():
    fast_api_env = os.getenv("FAST_API_ENV", "development")
    logger.info(">>> startup")
    logger.info('<' + '-' * 66 + '>')
    logger.info(f'时间: {datetime.datetime.now()}')
    logger.info(f'操作系统: {platform.system()}')
    logger.info(f'项目路径: {os.getcwd()}')
    logger.info(f'当前环境: {fast_api_env} (config: {project_config.ENV})')
    logger.info(f'父进程id: {os.getppid()}')
    logger.info(f'子进程id: {os.getpid()}')
    logger.info(f'线程id: {threading.get_ident()}')
    logger.info('<' + '-' * 66 + '>')


async def _init_db():
    logger.info(">>> Mysql连接池初始化")
    await Tortoise.init(config=TORTOISE_CONFIG)
    logger.info(">>> Tortoise ORM 初始化完成")


async def _init_redis():
    logger.info(">>> Redis连接池初始化")
    await create_redis_connection_pool()
    logger.debug(f"redis_pool: {redis_module.redis_pool!r}")
    logger.info(">>> Redis 连接池初始化完成")


async def _init_scheduler():
    await scheduler_init()
    logger.info(">>> 定时任务初始化")


async def _shutdown_scheduler():
    if getattr(scheduler, "running", False):
        try:
            with suppress(SchedulerNotRunningError):
                scheduler.shutdown(wait=False)
            logger.info(">>> 定时任务已关闭")
        except Exception:
            logger.exception(">>> 定时任务关闭失败")
    else:
        logger.info(">>> 定时任务未启动，跳过关闭")


async def _shutdown_redis():
    try:
        await close_redis_connection_pool()
        logger.info(">>> Redis 连接池已关闭")
    except Exception:
        logger.exception(">>> Redis 连接池关闭失败")


async def _shutdown_db():
    try:
        await Tortoise.close_connections()
        logger.info(">>> 数据库连接已关闭")
    except Exception:
        logger.exception(">>> 数据库连接关闭失败")


async def startup_event():
    """应用启动前执行"""

    _log_startup_info()
    logger.info(f'>>> Config初始化: {project_config.ENV}')

    try:
        await _init_db()
        await _init_redis()
        await _init_scheduler()
    except Exception:
        logger.exception("应用启动失败，开始回收资源")
        await _shutdown_scheduler()
        await _shutdown_redis()
        await _shutdown_db()
        raise


async def shutdown_event():
    """应用关闭后执行"""

    logger.info(">>> shutdown")
    await _shutdown_scheduler()
    await _shutdown_redis()
    await _shutdown_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    try:
        yield
    finally:
        await shutdown_event()
