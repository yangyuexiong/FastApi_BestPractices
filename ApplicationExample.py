# -*- coding: utf-8 -*-
# @Time    : 2024/2/2 17:05
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
from fastapi import FastAPI, APIRouter, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Header, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from tortoise import Tortoise

from app.api import api
from config.config import get_config
from common.libs.api_result import api_result
from utils.print_logs import print_logs, json_format
from utils.db_connect import db_init
from utils.redis_connect import create_redis_connection_pool, close_redis_connection_pool

from common.libs.custom_exception import CustomException

project_config = get_config()


# 调试
async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


# 调试
async def get_token_header(x_token: str = Header(), token: str = Header(), a_123: str = Header()):
    print(f"x_token:{x_token}")
    print(f"token:{token}")
    print(f"a_123:{a_123}")
    if x_token != "fake-super-secret-token":
        # raise HTTPException(status_code=400, detail="X-Token header invalid")
        raise CustomException(status_code=400, detail="Item not found", custom_code=1001, data=[123])


router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found 123"}},
)
fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/")
async def read_items():
    return {
        "code": 200,
        "message": "ok"
    }


@router.get("/{item_id}")
async def read_item(item_id: str):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"name": fake_items_db[item_id]["name"], "item_id": item_id}


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

        # token = request.headers.get('token')
        # if token != "":
        #     return api_result(401)

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


def create_app():
    """app实例"""

    app = FastAPI(
        title="FastApi_BestPractices",
        description="description",
        summary="I hope everything has best practices.",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        debug=True
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
        # print("request", request.__dict__)
        content = {
            "code": exc.custom_code,
            "message": exc.detail,
            "data": exc.data
        }
        if not exc.data:
            del content["data"]

        return JSONResponse(
            status_code=exc.status_code,
            content=content
        )

    # 路由注册
    app.include_router(router)
    app.include_router(api)

    return app


app = create_app()  # 用于执行以下代码调试使用，非用于其他文件导入使用。

if __name__ == '__main__':
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=9999)

    uvicorn.run("ApplicationExample:app", host="0.0.0.0", port=9999, reload=True)
