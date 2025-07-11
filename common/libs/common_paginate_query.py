# -*- coding: utf-8 -*-
# @Time    : 2024/4/28 18:02
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : common_paginate_query.py
# @Software: PyCharm

from typing import List, Dict
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from utils.utils import convert_to_standard_format
from common.libs.common_page import page_size, query_result


class JsonFieldHandle:
    """
    用于后续优化:
        CommonPaginateQuery.json_field_keys_to_obj
        CommonPaginateQuery.json_field_obj_to_keys
    """

    def __init__(self):
        pass


class CommonPaginateQuery:
    """通用分页模糊组合查询"""

    def __init__(self, request_data: BaseModel, orm_model, model_pydantic: BaseModel = None, like_list: list = None,
                 where_list: list = None, order_by_list: list = None, filter_range: dict = None,
                 json_field_keys_to_obj: List[Dict] = None, json_field_obj_to_keys: List[Dict] = None,
                 output_model: BaseModel = None, exclude_field: set = None, skip_list: List = None):
        """

        :param request_data: 入参模型
        :param orm_model: ORM模型
        :param model_pydantic:  使用`model_pydantic`处理`Model`数据
        :param like_list:   模糊查询字段
        :param where_list:  只需要传入字段的名称例如：["name", ...] 在逻辑中会通过`request_data`组装成`精确查询条件`
        :param order_by_list:   排序字段名称降序加"-"号, 升序["id", ...] 降序["-id", ...]
        :param filter_range:    范围查询条件,直接传入orm语法例如:{"create_time__gte": "","create_time__lte": "","last_login__isnull": False,...}
        :param json_field_keys_to_obj: 入参例子: [{"model":User, "query_key":"id", "field":"user_id_list","exclude_field":{"name","..."}},...]; 作用:JSON字段`id`列表转`obj`列表例如:[1,2,3] -> [<User>,...] 或者 [{"id":1,"name":"yyx"},...]
        :param json_field_obj_to_keys: 入参例子: [{"field":"user_id_list","key":"id"},...]; JSON字段`obj`列表转`id`列表例如:[{"id":1,"name":"yyx"},...] 转 [1,2,3...]
        :param output_model:    响应模型
        :param exclude_field:   忽略字段,例如: {"password","uuid",...}
        :param skip_list:       忽略值为`0`或`None`的字段判断,例如 is_deleted=0 不会被跳过
        """

        self.request_data = request_data
        self.orm_model = orm_model
        self.model_pydantic = model_pydantic
        self.like_list = like_list
        self.where_list = where_list
        self.order_by_list = order_by_list
        self.json_field_keys_to_obj = json_field_keys_to_obj
        self.json_field_obj_to_keys = json_field_obj_to_keys
        self.filter_range = filter_range
        self.output_model = output_model
        self.exclude_field = exclude_field

        self.filter_conditions = {}  # 模糊查询条件
        self.where_dict = {}  # 精确查询条件
        self.records = []  # 结果数据
        self.normal_data = []  # 默认结果数据组装

        # 忽略值为`0`或`None`的字段判断,例如 is_deleted=0 不会被跳过
        if skip_list:
            self.skip_list = skip_list + ["is_deleted"]
        else:
            self.skip_list = ["is_deleted"]

    async def build_filter_conditions(self):
        """构建模糊查询条件"""

        for k, v in self.request_data.dict().items():
            if v is None or bool(v) is False and k not in self.skip_list:
                continue
            if k in self.like_list:
                self.filter_conditions[f"{k}__icontains"] = v
            if k in self.where_list:
                self.where_dict[k] = v

        self.filter_conditions.update(self.where_dict)

    async def build_like(self):
        """构建迷糊查询字段"""

        if not self.like_list:
            self.like_list = []

    async def build_where(self):
        """构建查询条件"""

        if not self.where_list:
            self.where_list = []

    async def build_range(self):
        """构建范围条件"""

        if self.filter_range:
            for k, v in self.filter_range.items():
                if v == "":
                    del self.filter_range[k]

            self.filter_conditions.update(self.filter_range)

    async def build_order_by(self):
        """构建排序条件"""

        if not self.order_by_list:
            self.order_by_list = []

    async def build_query(self):
        """构建完整查询"""

        await self.build_like()
        await self.build_where()
        await self.build_filter_conditions()
        await self.build_range()
        await self.build_order_by()

        page = self.request_data.page
        now_page = page
        size = self.request_data.size
        page, size = await page_size(page, size)

        # 获取未分页之前的总数（带有查询条件）
        total_count = await self.orm_model.filter(**self.filter_conditions).count()

        # 分页查询（同样带有相同查询条件）
        model_list = await self.orm_model.filter(**self.filter_conditions).offset(page).limit(size).order_by(
            *self.order_by_list)

        for model in model_list:
            if hasattr(model, "create_time"):
                model.create_time = convert_to_standard_format(str(model.create_time))
            if hasattr(model, "update_time"):
                model.update_time = convert_to_standard_format(str(model.update_time))
            if hasattr(model, "go_live_time"):
                model.go_live_time = convert_to_standard_format(str(model.go_live_time))

            if self.json_field_keys_to_obj:
                for d in self.json_field_keys_to_obj:
                    d_field = d.get("field")
                    d_model = d.get("model")
                    d_query_key = d.get("query_key")
                    d_exclude_field = d.get("exclude_field")
                    if hasattr(model, d_field) and isinstance(getattr(model, d_field), list):
                        d_filter = {
                            f"{d_query_key}__in": getattr(model, d_field)
                        }
                        d_model_list = await d_model.filter(**d_filter).all()
                        if d_model_list:
                            setattr(model, d_field, jsonable_encoder(d_model_list, exclude=d_exclude_field))

            if self.json_field_obj_to_keys:  # 这个用的比较少, 后续再实现!
                pass

        # 将查询结果转换为 Pydantic 模型 (待弃用)
        if self.model_pydantic:
            model_list = [await self.model_pydantic.from_tortoise_orm(model) for model in model_list]

        if self.output_model:
            model_list = [self.output_model.from_orm(model).dict() for model in model_list]

        # 处理忽略字段
        if self.exclude_field and isinstance(self.exclude_field, set):
            self.records = jsonable_encoder(model_list, exclude=self.exclude_field)
        else:
            self.records = jsonable_encoder(model_list)

        # 将总数和分页后的结果一起传递给 query_result 函数
        data = await query_result(records=self.records, now_page=now_page, total=total_count)
        self.normal_data = data

        return self.normal_data
