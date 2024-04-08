# -*- coding: utf-8 -*-
# @Time    : 2024/4/8 18:06
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : api_result.py
# @Software: PyCharm

from fastapi.responses import JSONResponse


def get_response_message(code):
    """获取状态码对应的消息"""

    code_dict = {
        401: "未授权"
    }

    message = code_dict.get(code)
    if message:
        return message

    return None


def api_result(code=None, message=None, data=None, details=None, status=None):
    """
    返回格式
    :param code:
    :param message:
    :param data:
    :param details:
    :param status:
    :return:
    """

    if not message:
        message = get_response_message(code)

    result = {
        "code": code,
        "message": message,
        "data": data,
    }

    if not result.get('data'):
        result.pop('data')

    return JSONResponse(status_code=401, content=result)
