# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 15:33
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : print_logs.py
# @Software: PyCharm


import json

from loguru import logger


def get_req_ip(request):
    """ip"""

    ip = request.headers.get('X-Forwarded-For')
    if ip in ("127.0.0.1", None):
        return "0.0.0.0"
    return ip


def json_format(data):
    """json格式打印"""
    try:
        result = json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False)
        logger.info(f'\n{result}')
    except BaseException as e:
        logger.info(f'\n{data}')


async def print_logs(request):
    """美化日志输出"""

    host = request.client.host
    # ip_address = request.headers.get('X-Forwarded-For')
    ip_address = get_req_ip(request)
    method = request.method
    path = request.url.path
    headers = {t[0]: t[1] for t in request.headers.items()}
    is_multipart = headers.get("content-type", "").startswith("multipart/form-data")

    params = request.query_params
    try:
        if is_multipart:
            form_data = {}
        else:
            form_data = await request.form()
    except BaseException as e:
        form_data = {}

    if method != "GET":
        try:
            json_data = await request.json()
        except BaseException as e:
            json_data = {}
    else:
        json_data = {}

    logger.info(f"host:{host}")
    logger.info(f"ip_address:{ip_address}")
    logger.info(f"method:{method}")
    logger.info(f"path:{path}")

    logger.info('=== headers ===')
    json_format(headers)
    logger.info('=== params ===', type(params))
    json_format(params)
    logger.info('=== data ===', form_data)
    json_format(dict(form_data))
    logger.info('=== json ===', json_data)
    json_format(json_data)

    logger.info('=== end print_logs ===')
