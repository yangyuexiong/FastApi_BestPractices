# -*- coding: utf-8 -*-
# @Time    : 2024/5/10 14:34
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : common_pydantic_base.py
# @Software: PyCharm

from typing import Union
from pydantic import BaseModel, Field

"""
exclude_unset：是否排除未明确设置的字段。 
exclude_defaults：是否排除设置为默认值的字段。 
exclude_none：是否排除值为“None”的字段。
"""


class CommonPydanticCreate(BaseModel):
    remark: Union[str, None] = Field(default=None, description="备注", example="")
    creator: Union[str, None] = Field(default=None, description="创建人(不需要传,从鉴权获取)")
    creator_id: Union[int, None] = Field(default=None, description="创建人ID(不需要传,从鉴权获取)")

    def dict(self, **kwargs):
        """重写 dict() 方法，在每次调用时带上指定参数: exclude_unset=True"""
        return super().dict(exclude_unset=True, **kwargs)


class CommonPydanticUpdate(BaseModel):
    id: Union[int, None] = Field(default=None, description="需要编辑的数据ID", example="")
    remark: Union[str, None] = Field(default=None, description="备注", example="")
    modifier: Union[str, None] = Field(default=None, description="更新人(不需要传,从鉴权获取)")
    modifier_id: Union[int, None] = Field(default=None, description="更新人ID(不需要传,从鉴权获取)")

    def dict(self, **kwargs):
        """重写 dict() 方法，在每次调用时带上指定参数: exclude_unset=True, exclude_defaults=True, exclude_none=True"""
        return super().dict(exclude_unset=True, exclude_defaults=True, exclude_none=True, **kwargs)
