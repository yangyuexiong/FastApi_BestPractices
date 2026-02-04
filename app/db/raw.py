# -*- coding: utf-8 -*-
# @Time    : 2024/5/8 20:23
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : common_select.py
# @Software: PyCharm

from loguru import logger
from tortoise import Tortoise

from app.db.tortoise import db_init


async def select(sql: str, debug: bool = False, connection_key="default", *args):
    if debug:
        await db_init()

    if args:
        result = await Tortoise.get_connection(connection_key).execute_query_dict(sql, args)
    else:
        result = await Tortoise.get_connection(connection_key).execute_query_dict(sql)

    if debug:
        logger.debug(result)

    return result


if __name__ == '__main__':
    from tortoise import run_async

    sql1 = """
        SELECT * FROM msl_order AS A
        LEFT JOIN msl_order_item AS B ON A.id=B.order_id
        WHERE A.order_number=%s 
        AND B.openid=%s
        """
    field_list = ['202404281439151714286355', 'omScQ7XY4LM-FyCiJmJH6H9r2Zxo']
    # run_async(select(sql1, True, *field_list))

    sql = """
        SELECT
        *
    FROM
        bm_message_push_conf AS A
        LEFT JOIN bm_aps_tasks AS B ON A. `uuid` = B.task_id
    WHERE
        A.is_deleted = 0
        AND A.name LIKE "%123%"
        AND A.message_type='告警'
        AND A.push_type='邮箱'
    ORDER BY
        A.update_time DESC
    LIMIT 0,20;
    """
    run_async(select(sql, True, *[]))
