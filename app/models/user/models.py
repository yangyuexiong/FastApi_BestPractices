# -*- coding: utf-8 -*-
# @Time    : 2024/3/2 19:03
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : models.py
# @Software: PyCharm


from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from common.libs.base_model import CustomBaseModel


class User(CustomBaseModel):
    """用户"""

    username = fields.CharField(max_length=255, unique=True, description='用户名')
    password = fields.CharField(max_length=255, description='密码')
    creator = fields.CharField(max_length=32, null=True, description="创建人")
    creator_id = fields.BigIntField(null=True, description="创建人id")
    modifier = fields.CharField(max_length=32, null=True, description='更新人')
    modifier_id = fields.BigIntField(null=True, description='更新人id')
    remark = fields.CharField(max_length=255, null=True, description='备注')

    class Meta:
        table = "user"

    class PydanticMeta:
        exclude = ["password"]


User_Pydantic = pydantic_model_creator(User, name="User")
