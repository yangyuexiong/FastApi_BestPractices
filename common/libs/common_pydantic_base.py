# -*- coding: utf-8 -*-
# @Time    : 2024/5/10 14:34
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : common_pydantic_base.py
# @Software: PyCharm


from pydantic import BaseModel
from typing import Union

"""
exclude_unset：是否排除未明确设置的字段。 
exclude_defaults：是否排除设置为默认值的字段。 
exclude_none：是否排除值为“None”的字段。
"""


class CommonPydanticCreate(BaseModel):
    remark: Union[str, None] = None
    creator: Union[str, None] = None
    creator_id: Union[int, None] = None

    def dict(self, **kwargs):
        """重写 dict() 方法，在每次调用时带上指定参数: exclude_unset=True"""
        return super().dict(exclude_unset=True, **kwargs)


class CommonPydanticUpdate(BaseModel):
    id: Union[int, None] = None
    remark: Union[str, None] = None
    modifier: Union[str, None] = None
    modifier_id: Union[int, None] = None

    def dict(self, **kwargs):
        """重写 dict() 方法，在每次调用时带上指定参数: exclude_unset=True, exclude_defaults=True, exclude_none=True"""
        return super().dict(exclude_unset=True, exclude_defaults=True, exclude_none=True, **kwargs)
