# -*- coding: utf-8 -*-
# @Time    : 2024/8/24 15:52
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : admin_api.py
# @Software: PyCharm

import re
from typing import Optional, Union

from fastapi import APIRouter, Depends, Header, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from tortoise.expressions import Q

from app.core.exceptions import CustomException
from app.core.pagination import CommonPaginateQuery
from app.core.response import api_response
from app.core.security import check_admin_existence
from app.core.password import hash_password
from app.db.redis_client import delete_value
from app.models.admin import Admin
from app.schemas.common import CommonPydanticCreate, CommonPydanticUpdate
from app.schemas.pagination import CommonPage

router = APIRouter()

PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=\-{}|:;<>?,./]).{8,}$')


class CreateAdminReqData(CommonPydanticCreate):
    code: Optional[str] = Field(default=None, description="工号")
    username: str = Field(description="用户名", min_length=1)
    nickname: str = Field(description="昵称", min_length=1)
    mail: str = Field(description="邮件", min_length=1)
    phone: Union[str, int] = Field(description="手机号")
    password: str = Field(description="密码", min_length=8)


class UpdateAdminReqData(CommonPydanticUpdate):
    id: int = Field(description="需要编辑的数据ID")
    nickname: str = Field(default=None, description="昵称")
    mail: str = Field(default=None, description="邮件")
    phone: Union[str, int] = Field(description="手机号")


class DeleteAdminReqData(BaseModel):
    id: int = Field(description="主键ID")
    status: int = Field(description="状态")


class AdminPage(CommonPage):
    is_deleted: int = 0
    creator_id: Optional[int] = None
    code: Optional[str] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    mail: Optional[str] = None
    phone: Optional[str] = None


class ResetPasswordReqData(BaseModel):
    user_id: int
    new_password: str
    raw_password: str


async def validate_password(password):
    if not PASSWORD_REGEX.match(password):
        raise CustomException(detail="密码必须包含大小写字母数字符号，且长度不少于8位", custom_code=10001)
    return password


async def create_admin_validator(request_data: CreateAdminReqData) -> CreateAdminReqData:
    """Admin验证器"""

    username = request_data.username
    if not username:
        raise CustomException(detail="用户名不能为空", custom_code=10001)

    password = request_data.password
    if not password:
        raise CustomException(detail="密码不能为空", custom_code=10001)

    await validate_password(password)

    mail = request_data.mail
    if not mail:
        raise CustomException(detail="邮箱不能为空", custom_code=10001)

    # code = request_data.code
    phone = request_data.phone
    query_admin = await Admin.filter(
        # Q(code=code) | Q(username=username) | Q(mail=mail) | Q(phone=phone)
        Q(username=username) | Q(mail=mail) | Q(phone=phone)
    ).all()

    if query_admin:
        for admin in query_admin:
            if admin.username == username:
                raise CustomException(detail=f"用户名: {username} 已存在", custom_code=10003)
            elif admin.mail == mail:
                raise CustomException(detail=f"邮箱: {mail} 已存在", custom_code=10003)
            # elif admin.code == code:
            #     raise CustomException(detail=f"工号: {code} 已存在", custom_code=10003)
            elif admin.phone == str(phone):
                raise CustomException(detail=f"手机号: {phone} 已存在", custom_code=10003)

    return request_data


@router.get("/{admin_id}", summary="用户详情")
async def admin_detail(admin_id: int, admin: Admin = Depends(check_admin_existence)):
    """用户详情"""

    query_admin = await Admin.get_or_none(id=admin_id)
    if not query_admin:
        return api_response(code=10002, message=f"用户 {admin_id} 不存在")
    else:
        return api_response(data=jsonable_encoder(query_admin, exclude={"password"}))


@router.post("", summary="新增用户")
async def create_admin(
        request_data: CreateAdminReqData = Depends(create_admin_validator),
        admin: Admin = Depends(check_admin_existence)
):
    """新增用户"""

    request_data.creator_id = admin.id
    request_data.creator = admin.username
    save_data = request_data.dict()
    save_data["password"] = hash_password(request_data.password)
    await Admin.create(**save_data)
    return api_response(http_code=status.HTTP_201_CREATED, code=201)


@router.put("", summary="编辑用户")
async def update_admin(
        request_data: UpdateAdminReqData,
        admin: Admin = Depends(check_admin_existence)
):
    """编辑用户"""

    admin_id = request_data.id
    query_admin = await Admin.get_or_none(id=admin_id)
    if not query_admin:
        return api_response(code=10002, message=f"用户 {admin_id} 不存在")

    nickname = request_data.nickname
    if not nickname:
        raise CustomException(detail="昵称不能为空", custom_code=10001)

    mail = request_data.mail
    if not mail:
        raise CustomException(detail="邮箱不能为空", custom_code=10001)

    phone = request_data.phone
    query_admins = await Admin.filter(
        Q(nickname=nickname) | Q(mail=mail) | Q(phone=phone)
    ).all()

    if query_admins:
        for admin in query_admins:
            if admin.mail == mail and admin.id != admin_id:
                raise CustomException(detail=f"邮箱: {mail} 已存在", custom_code=10003)
            elif admin.nickname == nickname and admin.id != admin_id:
                raise CustomException(detail=f"昵称: {nickname} 已存在", custom_code=10003)
            elif str(admin.phone) == str(phone) and admin.id != admin_id:
                raise CustomException(detail=f"手机号: {phone} 已存在", custom_code=10003)

    request_data.modifier_id = admin.id
    request_data.modifier = admin.username
    update_data = request_data.dict()
    del update_data["id"]
    await query_admin.update_from_dict(update_data).save()
    return api_response(http_code=status.HTTP_201_CREATED, code=201)


@router.delete("", summary="删除(禁用)用户")
async def delete_admin(
        request_data: DeleteAdminReqData,
        admin: Admin = Depends(check_admin_existence)
):
    """删除(禁用)用户"""

    admin_id = request_data.id
    query_admin = await Admin.get_or_none(id=admin_id)
    if not query_admin:
        return api_response(code=10002, message=f"用户 {admin_id} 不存在")
    elif admin.id not in (1, 2, 3):
        return api_response(code=10002, message="无权限")
    elif query_admin.username == "admin":
        return api_response(code=10002, message=f"管理员账户不能被禁用")
    elif admin_id in (1, 2, 3):
        return api_response(code=10002, message=f"用户 {query_admin.username} 不能被禁用")
    else:
        ud = {
            # "is_deleted": admin_id,
            "modifier": admin.username,
            "modifier_id": admin.id,
            "status": request_data.status,
        }
        await query_admin.update_from_dict(ud).save()
        return api_response()


@router.post("/page", summary="用户列表")
async def admin_page(request_data: AdminPage, admin: Admin = Depends(check_admin_existence)):
    """用户列表"""

    pq = CommonPaginateQuery(
        request_data=request_data,
        orm_model=Admin,
        like_list=["code", "username", "nickname", "mail", "phone"],
        where_list=["creator_id", "is_deleted"],
        order_by_list=["-update_time"],
        exclude_field={"password"}
    )
    await pq.build_query()
    return api_response(data=pq.normal_data)


@router.post("/reset_password", summary="重置密码")
async def reset_password(request_data: ResetPasswordReqData, token: str = Header()):
    """重置密码"""

    admin_id = request_data.user_id
    query_admin = await Admin.get_or_none(id=admin_id)
    if not query_admin:
        return api_response(code=10002, message=f"用户 {admin_id} 不存在")

    if request_data.new_password != request_data.raw_password:
        return api_response(code=10005, message="两次输入密码不一致")

    await validate_password(request_data.new_password)
    await query_admin.set_password(request_data.new_password)
    await query_admin.save()
    await delete_value(token)
    return api_response(message="重置成功")
