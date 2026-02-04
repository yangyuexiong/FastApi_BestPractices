# -*- coding: utf-8 -*-
# @Time    : 2024/7/27 15:36
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : time_utils.py
# @Software: PyCharm

from datetime import datetime

from dateutil import parser


def convert_to_standard_format(datetime_str) -> str:
    """
    时间格式化处理
    输出例如: `2024-07-27 15:22:31`
    """

    try:
        if isinstance(datetime_str, datetime):
            return datetime_str.strftime('%Y-%m-%d %H:%M:%S')
        dt = parser.parse(datetime_str)  # 解析未知格式的日期时间字符串
        formatted_dt = dt.strftime('%Y-%m-%d %H:%M:%S')  # 将日期时间对象格式化为指定的格式
        return formatted_dt
    except BaseException as e:  # 异常返回原数据
        return datetime_str


def timestamp_to_datetime(timestamp) -> str:
    """时间戳转字符串日期"""

    # 将时间戳转换为datetime对象
    dt_object = datetime.fromtimestamp(timestamp)

    # 使用strftime方法将datetime对象格式化为字符串日期
    str_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return str_date


def datetime_to_timestamp(date_string, set_cn: bool = False, is_ms: bool = False):
    """
    结构化时间转时间戳

    :param date_string:
    :param set_cn: 服务器时区差补充
    :param is_ms: 使用毫秒(*1000)
    :return:
    """

    if not date_string:
        return 0

    # 定义日期时间字符串
    # date_string = "2023-10-09 20:00:00"

    # 将日期时间字符串转化为 datetime 对象
    datetime_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    # 获取时间戳
    timestamp = datetime_object.timestamp()
    if set_cn:
        handle_timestamp = int(timestamp) + 28800
    else:
        handle_timestamp = int(timestamp)

    if is_ms:
        return handle_timestamp * 1000
    else:
        return handle_timestamp


def today_zero_timestamp() -> int:
    """当天零点时间戳"""

    # 获取今天的日期
    today = datetime.now().date()

    # 创建今天00:00的datetime对象
    midnight = datetime.combine(today, datetime.min.time())

    # 获取时间戳
    timestamp = int(midnight.timestamp())

    return timestamp


if __name__ == '__main__':
    print(convert_to_standard_format("2024-07-27 15:45:30.292836+08"))
    print(convert_to_standard_format("2024-07-27T15:45:30"))
    print(convert_to_standard_format("2024-07-27 09:39:53.000000"))
    print(convert_to_standard_format("test error"))
    print(today_zero_timestamp())
    print(timestamp_to_datetime(today_zero_timestamp()))
    print(timestamp_to_datetime(today_zero_timestamp() + 86399))
