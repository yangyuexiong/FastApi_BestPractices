# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 14:29
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : main.py
# @Software: PyCharm

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_config
from app.core.exception_handlers import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.middleware import MyMiddleware

project_config = get_config()

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
        title="FastApi_BestPractices",
        description="description",
        summary="I hope everything has best practices.",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        lifespan=lifespan,
        **kw
    )

    # 跨域: 如果 allow_credentials=True，则 allow_origins 不能设置为 ["*"]，必须明确指定允许的域名。
    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # 中间件注册(全局拦截器)(一个或多个)
    """
    注册方式一:
    @app.middleware("http")
    async def middleware_1(request: Request, call_next):
        ...

    @app.middleware("http")
    async def middleware_2(request: Request, call_next):
        ...

    注册方式二:
    app.add_middleware(MyMiddleware)
    """

    app.add_middleware(
        MyMiddleware,
        log_headers=debug,
        log_body=debug,
        exclude_paths=["/docs", "/openapi.json", "/redoc", "/static*"],
        sensitive_headers=project_config.SENSITIVE_HEADERS,
        mask_sensitive_headers=project_config.MASK_SENSITIVE_HEADERS,
    )

    register_exception_handlers(app, debug)

    # 路由注册
    app.include_router(api_router)

    # 静态资源(生产环境通过配置获取路径)
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    return app


app = create_app()
