# -*- coding: utf-8 -*-
# @Time    : 2024/8/26 13:45
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : models.py
# @Software: PyCharm

from tortoise import fields

from app.models.base import CustomBaseModel


class ApsTask(CustomBaseModel):
    """定时任务"""

    task_id = fields.CharField(max_length=64, description="任务id")
    trigger_type = fields.CharField(max_length=16, description="触发器类型:date;interval;cron")
    trigger_param = fields.JSONField(description="触发器参数")
    task_function_name = fields.CharField(max_length=255, null=True, description="任务函数名称")
    task_function_args = fields.JSONField(default=[], description="任务参数:args")
    task_function_kwargs = fields.JSONField(default={}, description="任务参数:kwargs")

    class Meta:
        table = "fbp_aps_tasks"
