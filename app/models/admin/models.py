# -*- coding: utf-8 -*-
# @Time    : 2024/4/13 01:11
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : models.py
# @Software: PyCharm

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.context import CryptContext

from common.libs.base_model import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Admin(BaseModel):
    username = fields.CharField(max_length=20, unique=True, description='用户名')
    password = fields.CharField(max_length=255, description='密码')
    creator = fields.CharField(max_length=32, null=True, description="创建人")
    creator_id = fields.BigIntField(null=True, description="创建人id")
    modifier = fields.CharField(max_length=32, null=True, description='更新人')
    modifier_id = fields.BigIntField(null=True, description='更新人id')
    remark = fields.CharField(max_length=255, null=True, description='备注')

    # 设置密码时加密
    async def set_password(self, raw_password):
        self.password = pwd_context.hash(raw_password)

    # 验证密码
    async def verify_password(self, raw_password):
        return pwd_context.verify(raw_password, self.password)

    class Meta:
        table = "admin"

    class PydanticMeta:
        exclude = ["password"]


Admin_Pydantic = pydantic_model_creator(Admin, name="Admin")
