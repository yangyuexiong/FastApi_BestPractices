# -*- coding: utf-8 -*-
# @Time    : 2024/4/13 01:11
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : models.py
# @Software: PyCharm

from tortoise import fields

from common.libs.base_model import CustomBaseModel, create_custom_pydantic_model
from utils.password_context import pwd_context


class Admin(CustomBaseModel):
    """后台用户"""

    username = fields.CharField(max_length=255, unique=True, description='用户名')
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
        # print(f"raw_password:{raw_password}")
        # print(f"password:{self.password}")
        return pwd_context.verify(raw_password, self.password)

    class Meta:
        table = "admin"

    class PydanticMeta:
        exclude = ["password"]


"""
Admin_Pydantic = pydantic_model_creator(Admin, name="Admin")

from datetime import datetime

class Admin_Pydantic_Custom(Admin_Pydantic):
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")
        }

上述代码等价于:  Admin_Pydantic = create_custom_pydantic_model(Admin, name="Admin")
"""

Admin_Pydantic = create_custom_pydantic_model(Admin, name="Admin")
