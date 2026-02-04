# -*- coding: utf-8 -*-
# @Time    : 2026/2/4
# @Author  : yangyuexiong
# @File    : exception_handlers.py

from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.exceptions import CustomException


def register_exception_handlers(app: FastAPI, debug: bool):
    def _get_request_id(request: Request) -> Optional[str]:
        return getattr(request.state, "request_id", None) or request.headers.get("x-request-id")

    def _build_response(
        *,
        code: int,
        message: str,
        http_status: int,
        data: Any = None,
        request_id: Optional[str] = None,
    ) -> JSONResponse:
        content = {
            "code": code,
            "message": message,
            "data": data,
        }
        if data is None:
            content.pop("data")
        if request_id:
            content["request_id"] = request_id
        return JSONResponse(status_code=http_status, content=content)

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        request_id = _get_request_id(request)
        logger.bind(request_id=request_id).warning(f"CustomException: {exc.detail}")
        return _build_response(
            code=exc.custom_code,
            message=str(exc.detail),
            http_status=exc.status_code,
            data=exc.data,
            request_id=request_id,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = _get_request_id(request)
        logger.bind(request_id=request_id).info(f"HTTPException: {exc.detail}")
        return _build_response(
            code=exc.status_code,
            message=str(exc.detail),
            http_status=exc.status_code,
            request_id=request_id,
        )

    @app.exception_handler(Exception)
    async def base_exception_handler(request: Request, exc: Exception):
        request_id = _get_request_id(request)
        logger.bind(request_id=request_id).exception("Unhandled exception")
        data = [str(exc)] if debug else None
        return _build_response(
            code=500,
            message="Internal server error",
            http_status=500,
            data=data,
            request_id=request_id,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = _get_request_id(request)
        error_messages = []
        if debug:
            for error in exc.errors():
                error_messages.append({
                    "type": "validation_error",
                    "msg": error.get("msg"),
                    "loc": list(error.get("loc")),
                    "input": error.get("type"),
                })
        return _build_response(
            code=400,
            message="缺少必要的参数，参数类型错误",
            http_status=400,
            data=error_messages if debug else None,
            request_id=request_id,
        )
