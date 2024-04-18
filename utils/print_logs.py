# -*- coding: utf-8 -*-
# @Time    : 2024/4/8 16:47
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : print_logs.py
# @Software: PyCharm


import json

from loguru import logger


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
    ip_address = request.headers.get('X-Forwarded-For')
    method = request.method
    path = request.url.path
    headers = {t[0]: t[1] for t in request.headers.items()}

    params = request.query_params
    form_data = await request.form()

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
