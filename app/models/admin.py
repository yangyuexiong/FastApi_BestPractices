# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 15:09
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : models.py
# @Software: PyCharm

from tortoise import fields

from app.core.password import hash_password, verify_password
from app.models.base import CustomBaseModel


class Admin(CustomBaseModel):
    """后台用户"""

    username = fields.CharField(max_length=255, null=True, description='用户名')
    password = fields.CharField(max_length=255, description='密码')
    nickname = fields.CharField(max_length=128, null=True, description='昵称')
    phone = fields.CharField(max_length=64, null=True, description='手机号')
    mail = fields.CharField(max_length=256, null=True, description='邮箱')
    code = fields.CharField(max_length=64, null=True, description='用户编号')
    seat = fields.CharField(max_length=64, null=True, description='座位编号')
    department = fields.CharField(max_length=64, null=True, description='部门')
    position = fields.CharField(max_length=64, null=True, description='职位')
    superior = fields.CharField(max_length=64, null=True, description='上级')
    login_type = fields.CharField(max_length=64, null=True, default='single', description='登录类型:single;many')
    is_tourist = fields.IntField(default=1, description='0-游客账户;1-非游客账户')
    creator = fields.CharField(max_length=32, null=True, description="创建人")
    creator_id = fields.BigIntField(null=True, description="创建人id")
    modifier = fields.CharField(max_length=32, null=True, description='更新人')
    modifier_id = fields.BigIntField(null=True, description='更新人id')
    remark = fields.CharField(max_length=255, null=True, description='备注')

    # 设置密码时加密
    async def set_password(self, raw_password):
        self.password = hash_password(raw_password)

    # 验证密码
    async def verify_password(self, raw_password):
        return verify_password(raw_password, self.password)

    class Meta:
        table = "fbp_admin"

    class PydanticMeta:
        exclude = ["password"]
