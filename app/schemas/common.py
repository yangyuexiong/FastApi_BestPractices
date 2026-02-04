# -*- coding: utf-8 -*-
# @Time    : 2024/5/10 14:34
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : common_pydantic_base.py
# @Software: PyCharm

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

"""
exclude_unset：是否排除未明确设置的字段。 
exclude_defaults：是否排除设置为默认值的字段。 
exclude_none：是否排除值为“None”的字段。
"""


class CommonPydanticCreate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    remark: Optional[str] = Field(default=None, description="备注", examples=[""])
    creator: Optional[str] = Field(default=None, description="创建人(不需要传,从鉴权获取)")
    creator_id: Optional[int] = Field(default=None, description="创建人ID(不需要传,从鉴权获取)")

    def dict(self, **kwargs):
        """默认排除未设置字段"""
        return super().model_dump(exclude_unset=True, **kwargs)


class CommonPydanticUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    id: Optional[int] = Field(default=None, description="需要编辑的数据ID", examples=[1])
    remark: Optional[str] = Field(default=None, description="备注", examples=[""])
    modifier: Optional[str] = Field(default=None, description="更新人(不需要传,从鉴权获取)")
    modifier_id: Optional[int] = Field(default=None, description="更新人ID(不需要传,从鉴权获取)")

    def dict(self, **kwargs):
        """默认排除未设置/默认/空值字段"""
        return super().model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True, **kwargs)
