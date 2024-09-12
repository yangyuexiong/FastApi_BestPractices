# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 14:29
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : ApplicationExample.py
# @Software: PyCharm

import os
import time
import datetime
import platform
import threading

import shortuuid
from loguru import logger
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from tortoise import Tortoise

from app.api import api
from config.config import get_config
from utils.print_logs import print_logs, json_format
from utils.db_connect import db_init
from utils.redis_connect import create_redis_connection_pool, close_redis_connection_pool
from utils.scheduled_tasks.task_handler import scheduler, scheduler_init
# from g import global_object_init, GlobalObject

from common.libs.custom_exception import CustomException

project_config = get_config()


class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info('before_request')
        await print_logs(request)

        logger.info('api_after_request')
        start_time = time.time()
        log_uuid = f"{int(start_time)}_{shortuuid.uuid()}"
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Log-UUID"] = log_uuid
        resp_headers = {t[0]: t[1] for t in response.headers.items()}
        logger.info('=== resp_headers ===')
        json_format(resp_headers)

        return response


async def startup_event():
    """应用启动前执行"""

    print(">>> startup")
    fast_api_env = os.getenv("FAST_API_ENV", "development")
    print('<', '-' * 66, '>')
    print(f'时间:{datetime.datetime.now()}')
    print(f'操作系统:{platform.system()}')
    print(f'项目路径:{os.getcwd()}')
    print(f'当前环境:{fast_api_env}')
    print(f'父进程id:{os.getppid()}')
    print(f'子进程id:{os.getpid()}')
    print(f'线程id:{threading.get_ident()}')
    print('<', '-' * 66, '>')

    print(f'>>> Config初始化:{project_config.ENV}')

    print(">>> Mysql连接池初始化")
    await db_init()

    print(">>> Redis连接池初始化")
    await create_redis_connection_pool()
    import utils.redis_connect as rp
    print(rp.redis_pool, type(rp.redis_pool), id(rp.redis_pool))

    # print(">>> 全局对象初始化")
    # await global_object_init()

    # scheduler.start()
    await scheduler_init()
    print(">>> 定时任务初始化")


async def shutdown_event():
    """应用关闭后执行"""

    print(">>> shutdown")

    # 关闭 Tortoise ORM 连接
    await Tortoise.close_connections()

    # 关闭 Redis 连接
    import utils.redis_connect as rp
    print(rp.redis_pool, type(rp.redis_pool), id(rp.redis_pool))
    await close_redis_connection_pool()
    print(rp.redis_pool, type(rp.redis_pool), id(rp.redis_pool))

    # 关闭定时任务
    scheduler.shutdown()


def create_app():
    """app实例"""

    debug = project_config.DEBUG
    kw = {
        "debug": debug
    }

    # if not debug:  # `debug`为`False`时关闭接口文档访问
    #     kw["docs_url"] = None
    #     kw["redoc_url"] = None

    print(kw)
    app = FastAPI(
        title="Exile Chat",
        description="description",
        summary="I hope everything has best practices.",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        **kw
    )

    # 跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # 事件注册(应用启动前，或应用关闭后执行的事件处理器)(一个或多个)
    """
    装饰器写法:
    @app.on_event("startup")
    async def startup_event():
        print(">>> startup")

        app.state.app = app # 绑定 app或其他属性 到 request.app

    @app.on_event("shutdown")
    def shutdown_event():
        print(">>> shutdown")

    应用实例注册写法:
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)
    """
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)

    # 中间件注册(全局拦截器)(一个或多个)
    """
    注册方式一:
    @app.middleware("http")
    async def middleware_1(request: Request, call_next):
        print("before_request")
        start_time = time.time()
        log_uuid = f"{int(start_time)}_{shortuuid.uuid()}"
        print(log_uuid)
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Log-UUID"] = log_uuid
        return response

    @app.middleware("http")
    async def middleware_2(request: Request, call_next):
        ...

    注册方式二:
    app.add_middleware(MyMiddleware)
    """

    app.add_middleware(MyMiddleware)

    # 使用 app.add_exception_handler 方法添加异常处理程序
    # app.add_exception_handler(HTTPException, custom_exception_handler)

    # 注册自定义异常处理器
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request, exc: CustomException):
        content = {
            "code": exc.custom_code,
            "message": exc.detail,
            "data": exc.data
        }
        if not exc.data:
            del content["data"]

        return JSONResponse(status_code=exc.status_code, content=content)

    # 基础异常处理器,在`app.debug`为`False`时(生产环境)返回JSON, 为`True`时(开发环境)抛出堆栈信息
    @app.exception_handler(Exception)
    async def base_exception_handler(request: Request, exc: Exception):
        content = {
            "code": 500,
            "message": "Internal server error",
            "data": [str(exc)]
        }
        return JSONResponse(status_code=500, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        if debug:
            error_messages = []
            for error in exc.errors():
                error_messages.append({
                    "type": "validation_error",
                    "msg": error.get("msg"),
                    "loc": list(error.get("loc")),
                    "input": error.get("type"),
                    "debug": debug
                })

            content = {
                "code": 400,
                "message": "缺少必要的参数，参数类型错误",
                "data": error_messages
            }
            return JSONResponse(status_code=400, content=content)

        content = {
            "code": 400,
            "message": "缺少必要的参数，参数类型错误",
            "data": {
                "debug": debug
            }
        }
        return JSONResponse(status_code=400, content=content)

    # 路由注册
    app.include_router(api)

    # 静态资源(生产环境通过配置获取路径)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    return app
