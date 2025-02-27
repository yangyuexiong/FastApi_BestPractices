# -*- coding: utf-8 -*-
# @Time    : 2024/8/24 15:52
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : admin_api.py
# @Software: PyCharm

import re

from tortoise.expressions import Q

from all_reference import *
from app.models.admin.models import Admin, hash_password

admin_router = APIRouter()


class CreateAdminReqData(CommonPydanticCreate):
    code: str | None = None
    username: str
    nickname: str
    mail: str
    phone: str | int
    password: str


class UpdateAdminReqData(CommonPydanticUpdate):
    nickname: str
    mail: str
    phone: str | int


class DeleteAdminReqData(BaseModel):
    id: int
    status: str | int


class AdminPage(CommonPage):
    is_deleted: int = 0
    creator_id: Union[int, None] = None
    code: Union[str, None] = None
    username: Union[str, None] = None
    nickname: Union[str, None] = None
    mail: Union[str, None] = None
    phone: Union[str, None] = None


class ResetPasswordReqData(CommonPydanticUpdate):
    user_id: int
    new_password: str
    raw_password: str


async def validate_password(password):
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=\-{}|:;<>?,./]).{8,}$', password):
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


@admin_router.get("/{admin_id}")
async def admin_detail(admin_id: int, admin: Admin = Depends(check_admin_existence)):
    """用户详情"""

    query_admin = await Admin.get_or_none(id=admin_id)
    if not query_admin:
        return api_response(code=10002, message=f"用户 {admin_id} 不存在")
    else:
        return api_response(data=jsonable_encoder(query_admin, exclude={"password"}))


@admin_router.post("")
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


@admin_router.put("")
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
            print(admin.phone, type(admin.phone), phone, type(phone))
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


@admin_router.delete("")
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


@admin_router.post("/page")
async def admin_page(request_data: AdminPage, admin: Admin = Depends(check_admin_existence)):
    """用户列表"""

    data = await cpq(
        request_data, Admin,
        None,
        ["code", "username", "nickname", "mail", "phone"],
        ["creator_id", "is_deleted"],
        ["-update_time"],
        {"password"}
    )
    return api_response(data=data)


@admin_router.post("/reset_password")
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
