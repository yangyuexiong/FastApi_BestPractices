# -*- coding: utf-8 -*-
# @Time    : 2024/4/13 01:12
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : base_model.py
# @Software: PyCharm

import time
from datetime import datetime

import pytz
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class CustomBaseModel(models.Model):
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
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间(结构化时间)')
    create_timestamp = fields.BigIntField(default=int(time.time()), description='创建时间(时间戳)')
    update_time = fields.DatetimeField(description='更新时间(结构化时间)')
    update_timestamp = fields.BigIntField(null=True, description='更新时间(时间戳)')
    is_deleted = fields.BigIntField(default=0, description='0正常;其他:已删除')
    status = fields.IntField(default=1, description='状态')

    async def save(self, *args, **kwargs):
        """重写save方法，将时间字段转换为中国时区"""

        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        now_timestamp = int(now.timestamp())

        if self.id is None:
            self.create_time = now
            self.create_timestamp = now_timestamp

        self.update_time = now
        self.update_timestamp = now_timestamp

        await super().save(*args, **kwargs)

    class Meta:
        abstract = True


def create_custom_pydantic_model(model, name):
    """自定义:pydantic_model_creator"""

    # 使用 pydantic_model_creator 创建原始的 Pydantic 模型
    original_pydantic_model = pydantic_model_creator(model, name=name)

    # 定义自定义的 Pydantic 模型，继承自原始的 Pydantic 模型
    class CustomPydanticModel(original_pydantic_model):
        class Config:
            json_encoders = {
                datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")
            }

    return CustomPydanticModel
