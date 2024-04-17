# -*- coding: utf-8 -*-
# @Time    : 2024/4/13 18:43
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : admin_api.py
# @Software: PyCharm

from all_reference import *

from app.models.admin.models import Admin, Admin_Pydantic
from utils.password_context import pwd_context

admin_router = APIRouter()


class AdminCreate(BaseModel):
    username: str = "yyx"
    password: str = "123456"
    nickname: str = "昵称-xxx"
    phone: str = "15011111111"
    mail: str = "yang6333yyx@126.com"
    code: str = "00001"
    seat: str = "A666"
    remark: str = "新增备注"


class AdminUpdateData(BaseModel):
    nickname: str = "昵称-xxx"
    phone: str = "15012345678"
    mail: str = "yang6333yyx@126.com"
    code: str = "00001"
    seat: str = "A333"
    remark: str = "编辑备注"


class AdminUpdate(BaseModel):
    id: int = 1
    admin_data: AdminUpdateData


class AdminDelete(BaseModel):
    id: int = 1


class AdminPage(CommonPage):
    username: str = "admin"
    creator_id: int = 0


class AdminOut(BaseModel):
    create_time: datetime
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")
        }
    )


@admin_router.get("/{admin_id}")
async def admin_pofile(admin_id: int):
    """admin个人信息"""

    admin = await Admin.get_or_none(id=admin_id)

    if not admin:
        content = api_result(code=10002, message=f"管理员用户 {admin_id} 不存在")
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)
    else:
        admin_pydantic = await Admin_Pydantic.from_tortoise_orm(admin)
        content = api_result(code=status.HTTP_200_OK, data=jsonable_encoder(admin_pydantic))

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@admin_router.post("/")
async def create_admin(request_data: AdminCreate):
    """新增admin账号"""

    admin_username = request_data.username
    admin = await Admin.filter(username=admin_username).first()

    if admin:
        content = api_result(code=10003, message=f"管理员用户 {admin_username} 已存在")
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)
    else:
        # 加密密码
        hashed_password = pwd_context.hash(request_data.password)
        request_data.password = hashed_password

        # 创建新的管理员账号
        new_admin = await Admin.create(**request_data.dict(exclude_unset=True))
        new_admin_pydantic = await Admin_Pydantic.from_tortoise_orm(new_admin)
        content = api_result(code=status.HTTP_201_CREATED, data=jsonable_encoder(new_admin_pydantic))
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=content)


@admin_router.put("/")
async def update_admin(request_data: AdminUpdate):
    """更新admin信息"""

    admin_id = request_data.id
    admin_data = request_data.admin_data
    admin = await Admin.get_or_none(id=admin_id)

    if not admin:
        content = api_result(code=10002, message=f"管理员用户 {admin_id} 不存在")
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)
    else:
        await admin.update_from_dict(admin_data.dict(exclude_unset=True)).save()
        admin_result = await Admin_Pydantic.from_tortoise_orm(admin)
        content = api_result(code=status.HTTP_200_OK, data=jsonable_encoder(admin_result))
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@admin_router.delete("/")
async def delete_admin(request_data: AdminDelete):
    """删除(禁用)admin"""

    admin_id = request_data.id
    admin = await Admin.get_or_none(id=admin_id)

    if not admin:
        content = api_result(code=10002, message=f"管理员用户 {admin_id} 不存在")
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)
    else:
        await admin.update_from_dict({"is_deleted": admin_id}).save()
        content = api_result(code=status.HTTP_200_OK)
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@admin_router.post("/admin_page")
async def admin_page(request_data: AdminPage):
    """admin列表"""

    q = {
        # "username": request_data.username
        "username__icontains": request_data.username
    }
    if request_data.creator_id:
        q["creator_id"] = request_data.creator_id

    print(q)

    page = request_data.page
    size = request_data.size
    page, size = await page_size(page, size)

    admins = await Admin.filter(**q).offset(page).limit(size)
    print(admins)

    admins_pydantic = [await Admin_Pydantic.from_tortoise_orm(admin) for admin in admins]
    content = api_result(code=status.HTTP_200_OK, data=jsonable_encoder(admins_pydantic), is_pop=False)
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)
