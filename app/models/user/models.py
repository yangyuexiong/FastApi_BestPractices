# -*- coding: utf-8 -*-
# @Time    : 2024/3/2 19:03
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : models.py
# @Software: PyCharm


import time

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Users(models.Model):
    """
    The User model
    """

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    username2 = fields.CharField(max_length=20, unique=True)
    username3 = fields.CharField(max_length=20, unique=True)
    name = fields.CharField(max_length=50, null=True)
    family_name = fields.CharField(max_length=50, null=True)
    category = fields.CharField(max_length=30, default="misc")
    password_hash = fields.CharField(max_length=128, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    def full_name(self) -> str:
        """
        Returns the best name
        """
        if self.name or self.family_name:
            return f"{self.name or ''} {self.family_name or ''}".strip()
        return self.username

    class PydanticMeta:
        computed = ["full_name"]
        exclude = ["password_hash"]

    class Meta:
        table = "users"


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CustomDatetimeField(fields.DatetimeField):
    class _db_mysql(fields.DatetimeField._db_mysql):
        SQL_TYPE = "DATETIME"


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
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间(结构化时间)')
    create_timestamp = fields.BigIntField(default=int(time.time()), description='创建时间(时间戳)')
    update_time = fields.DatetimeField(auto_now=True, description='更新时间(结构化时间)')
    update_timestamp = fields.BigIntField(auto_now=True, null=True, description='更新时间(时间戳)')
    is_deleted = fields.BigIntField(default=0, description='0正常;其他:已删除')
    status = fields.IntField(default=1, description='状态')

    class Meta:
        abstract = True


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
# User_Pydantic = pydantic_model_creator(Users, name="User")
# UserIn_Pydantic = pydantic_model_creator(Users, name="UserIn", exclude_readonly=True)
