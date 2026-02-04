# -*- coding: utf-8 -*-
# @Time    : 2024/4/13 01:12
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : base_model.py
# @Software: PyCharm

import time
from datetime import datetime
from decimal import Decimal

import pytz
from loguru import logger
from tortoise import fields, models

TZ = pytz.timezone("Asia/Shanghai")


def now_tz() -> datetime:
    """获取当前时区时间"""
    return datetime.now(TZ)


def to_tz(dt: datetime) -> datetime:
    """将 datetime 转换为目标时区"""
    if dt.tzinfo is None:
        return TZ.localize(dt)
    return dt.astimezone(TZ)


class CustomDatetimeField(fields.DatetimeField):
    """自定义DatetimeField"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_value(self, value):
        """
        统一返回带时区的 datetime 对象
        """
        super_value = super().to_python_value(value)
        if super_value is None:
            return None
        if isinstance(super_value, datetime):
            return to_tz(super_value)
        return super_value


"""
使用MySql时,使用`CustomDatetimeField`
    create_time = CustomDatetimeField(auto_now_add=True, description='创建时间(结构化时间)')
    update_time = CustomDatetimeField(description='更新时间(结构化时间)')
    
使用Postgres时,使用`fields.DatetimeField`
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间(结构化时间)')
    update_time = fields.DatetimeField(description='更新时间(结构化时间)')
"""


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
    create_time = CustomDatetimeField(auto_now_add=True, description='创建时间(结构化时间)')
    create_timestamp = fields.BigIntField(default=lambda: int(time.time()), description='创建时间(时间戳)')
    update_time = CustomDatetimeField(description='更新时间(结构化时间)')
    update_timestamp = fields.BigIntField(null=True, description='更新时间(时间戳)')
    is_deleted = fields.BigIntField(default=0, null=True, description='0正常;其他:已删除')
    status = fields.IntField(default=1, null=True, description='状态')

    async def inject_save(self):
        """注入字段处理"""

    async def save(self, *args, **kwargs):
        """重写save方法，将时间字段转换为中国时区"""

        now = now_tz()
        now_timestamp = int(now.timestamp())

        if self.id is None:
            self.create_time = now
            self.create_timestamp = now_timestamp

        self.update_time = now
        self.update_timestamp = now_timestamp

        await self.inject_save()

        await super().save(*args, **kwargs)

    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if isinstance(value, datetime):  # 转换到 Asia/Shanghai 时区
            try:
                return to_tz(value)
            except Exception:
                logger.opt(exception=True).debug("datetime 时区转换失败")
                return value
        if isinstance(value, Decimal):
            return float(value)
        return value

    class Meta:
        abstract = True
