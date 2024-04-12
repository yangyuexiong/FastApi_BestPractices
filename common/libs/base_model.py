# -*- coding: utf-8 -*-
# @Time    : 2024/4/13 01:12
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : base_model.py
# @Software: PyCharm

import time

from tortoise import fields, models


class BaseModel(models.Model):
    """
    id:id
    create_timestamp:创建时间戳
    create_time:创建时间DateTime
    update_timestamp:更新时间戳
    update_time:更新时间DateTime
    is_deleted:是否删除
    status:状态
    """

    id = fields.BigIntField(pk=True, generated=True, description='id')
    create_time = fields.DatetimeField(auto_now_add=True, precision=0, description='创建时间(结构化时间)')
    create_timestamp = fields.BigIntField(default=int(time.time()), description='创建时间(时间戳)')
    update_time = fields.DatetimeField(auto_now=True, description='更新时间(结构化时间)')
    update_timestamp = fields.BigIntField(auto_now=True, null=True, description='更新时间(时间戳)')
    is_deleted = fields.BigIntField(default=0, description='0正常;其他:已删除')
    status = fields.IntField(default=1, description='状态')

    class Meta:
        abstract = True
