# -*- coding: utf-8 -*-
# @Time    : 2024/4/8 18:06
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : api_result.py
# @Software: PyCharm

from fastapi.responses import JSONResponse
from fastapi import status as fastapi_status


def custom_http_dict(custom_code):
    """自定义http响应消息字典"""

    code_dict = {
        200: "操作成功",
        201: "创建成功",
        203: "编辑成功",
        204: "删除成功",
        401: "未授权",
        10001: "必传参数",
        10002: "未找到数据",
        10003: "唯一校验",
        10004: "参数类型错误",
        10005: "业务校验错误",
        10006: "请求参数错误",
        10007: "未公开使用，非创建人，无法修改。",
    }

    message = code_dict.get(custom_code)
    if message:
        return message

    return None


def api_result(code: int = None, message: str = None, data: any = None, details: str = None,
               status: int = None, is_pop: bool = True) -> dict:
    """
    返回格式
    :param code:
    :param message:
    :param data:
    :param details:
    :param status:
    :param is_pop:
    :return:
    """

    if not message:
        message = custom_http_dict(code)

    result = {
        "code": code,
        "message": message,
        "data": data,
    }

    if not result.get('data') and is_pop:
        result.pop('data')

    return result
