# -*- coding: utf-8 -*-
# @Time    : 2026/2/4
# @Author  : yangyuexiong
# @File    : middleware.py

import json
import time
from typing import Iterable, Optional, Union

import shortuuid
from loguru import logger
from starlette.types import ASGIApp, Receive, Scope, Send

def _decode_headers(raw_headers) -> dict:
    # ASGI 原始 headers 为 bytes，这里统一转小写并解码
    return {k.decode().lower(): v.decode() for k, v in raw_headers}


def _mask_headers(headers: dict, sensitive_headers: set, mask: bool) -> dict:
    # 对敏感头做掩码处理，避免泄露
    if not mask:
        return headers
    return {k: ("***" if k in sensitive_headers else v) for k, v in headers.items()}


def _parse_header_list(value: Union[str, Iterable[str], None]) -> set:
    if not value:
        return set()
    if isinstance(value, str):
        return {h.strip().lower() for h in value.split(",") if h.strip()}
    return {str(h).strip().lower() for h in value if str(h).strip()}


def _get_client_ip(headers: dict, client) -> str:
    # 优先使用 X-Forwarded-For（反向代理场景），否则回退到 socket client
    xff = headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if client:
        return client[0]
    return "0.0.0.0"


class RequestLoggingMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        log_headers: bool = False,
        log_body: bool = False,
        max_body_size: int = 1024 * 1024,
        exclude_paths: Optional[Iterable[str]] = None,
        sensitive_headers: Union[str, Iterable[str], None] = None,
        mask_sensitive_headers: bool = True,
    ):
        self.app = app
        self.log_headers = log_headers
        self.log_body = log_body
        self.max_body_size = max_body_size
        self.exclude_paths = set(exclude_paths or [])
        self.sensitive_headers = _parse_header_list(sensitive_headers)
        self.mask_sensitive_headers = mask_sensitive_headers

    def _is_excluded(self, path: str) -> bool:
        # 支持精确匹配与简单前缀匹配（以 * 结尾）
        for p in self.exclude_paths:
            if p.endswith("*") and path.startswith(p[:-1]):
                return True
            if path == p:
                return True
        return False

    def _should_read_body(self, method: str, headers: dict) -> bool:
        # 只在需要时读取 body，避免对 GET/OPTIONS 等造成额外消耗
        if not self.log_body:
            return False
        if method in {"GET", "HEAD", "OPTIONS"}:
            return False
        content_type = headers.get("content-type", "").lower()
        if content_type.startswith("multipart/form-data"):
            # 文件上传不读取 body，避免大内存占用
            return False
        try:
            content_length = int(headers.get("content-length", "0") or 0)
        except ValueError:
            return False
        if content_length <= 0 or content_length > self.max_body_size:
            # 空 body 或超限直接跳过
            return False
        return True

    async def _receive_body(self, receive: Receive) -> bytes:
        # 读取完整请求体（需要重建 receive 供下游再次读取）
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] != "http.request":
                continue
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
        return body

    def _build_receive(self, body: bytes) -> Receive:
        # 构造新的 receive，让下游还能拿到 body
        sent = False

        async def receive() -> dict:
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.request", "body": b"", "more_body": False}

        return receive

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if self._is_excluded(path):
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        headers = _decode_headers(scope.get("headers", []))
        method = scope.get("method", "")
        query_string = scope.get("query_string", b"").decode()
        client = scope.get("client")
        # 优先复用上游请求 ID，没有则生成
        request_id = headers.get("x-request-id") or headers.get("x-log-uuid") or shortuuid.uuid()
        scope.setdefault("state", {})["request_id"] = request_id

        body = b""
        if self._should_read_body(method, headers):
            body = await self._receive_body(receive)
            receive = self._build_receive(body)

        status_code = None
        response_headers = []

        async def send_wrapper(message):
            nonlocal status_code, response_headers
            if message["type"] == "http.response.start":
                status_code = message.get("status")
                response_headers = list(message.get("headers", []))
                process_time = time.perf_counter() - start
                # 注入耗时与请求 ID，方便链路追踪
                response_headers.append((b"x-process-time", f"{process_time:.6f}".encode()))
                if not any(k.lower() == b"x-request-id" for k, _ in response_headers):
                    response_headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = response_headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            logger.exception("请求处理异常")
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            full_path = f"{path}?{query_string}" if query_string else path
            ip = _get_client_ip(headers, client)
            # 统一结构化访问日志
            logger.info(
                f"{method} {full_path} {status_code} {elapsed_ms:.2f}ms "
                f"ip={ip} rid={request_id}"
            )
            if self.log_headers:
                # 调试模式下可输出头信息（已脱敏）
                logger.debug(
                    f"headers: {_mask_headers(headers, self.sensitive_headers, self.mask_sensitive_headers)}"
                )
            if self.log_body and body:
                content_type = headers.get("content-type", "").lower()
                body_text = body.decode("utf-8", errors="replace")
                if "application/json" in content_type:
                    # JSON 尝试解析为对象便于阅读
                    try:
                        body_data = json.loads(body_text)
                    except Exception:
                        body_data = body_text
                else:
                    body_data = body_text
                logger.debug(f"body: {body_data}")


MyMiddleware = RequestLoggingMiddleware
