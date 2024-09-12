# -*- coding: utf-8 -*-
# @Time    : 2024/4/8 18:06
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : api_result.py
# @Software: PyCharm

from fastapi.responses import JSONResponse

from utils.utils import convert_to_standard_format


def custom_http_dict(custom_code):
    """自定义http响应消息字典"""

    code_dict = {
        200: "操作成功",
        201: "创建成功",
        203: "编辑成功",
        204: "删除成功",
        401: "未授权",
        500: '服务器异常',
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


def api_response(http_code: int = 200, code: int = 200, message: str = None, data: any = None,
                 datetime_format: bool = True, is_pop: bool = True) -> JSONResponse:
    """
    通用返回方式
    :param http_code: HTTP 状态码
    :param code: 自定义业务状态码
    :param message: 响应描述
    :param data: 响应数据
    :param datetime_format: 处理`data`中时间字段最终的输出格式: `2024-07-27 18:43:59`
    :param is_pop: 是否去除`data`的空数据, 例如: {"data":[]},{"data":{}},{"data":""}
    :return:
    """

    if not message:
        message = custom_http_dict(code)

    if data and isinstance(data, dict) and datetime_format:  # 默认字段名称:`create_time`;`update_time`根据需要补充

        if data.get("create_time"):
            data["create_time"] = convert_to_standard_format(data["create_time"])

        if data.get("update_time"):
            data["update_time"] = convert_to_standard_format(data["update_time"])

    content = {
        "code": code,
        "message": message,
        "data": data,
    }

    if not content.get('data') and is_pop:
        content.pop('data')

    return JSONResponse(status_code=http_code, content=content)
