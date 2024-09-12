# -*- coding: utf-8 -*-
# @Time    : 2024/5/8 20:23
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : common_select.py
# @Software: PyCharm

from tortoise import Tortoise

from utils.db_connect import db_init


async def select(sql: str, debug: bool = False, *args):
    if debug:
        await db_init()

    if args:
        result = await Tortoise.get_connection('default').execute_query_dict(sql, args)
    else:
        result = await Tortoise.get_connection('default').execute_query_dict(sql)

    if debug:
        print(result)

    return result


if __name__ == '__main__':
    from tortoise import run_async

    sql = """
        SELECT * FROM msl_order AS A
        LEFT JOIN msl_order_item AS B ON A.id=B.order_id
        WHERE A.order_number=%s 
        AND B.openid=%s
        """
    field_list = ['202404281439151714286355', 'omScQ7XY4LM-FyCiJmJH6H9r2Zxo']
    # run_async(select(sql, True, *field_list))
    run_async(select(sql, True, *[]))
