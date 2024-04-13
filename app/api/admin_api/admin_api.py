# -*- coding: utf-8 -*-
# @Time    : 2024/4/13 18:43
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : admin_api.py
# @Software: PyCharm


from all_reference import *

from app.models.admin.models import Admin, Admin_Pydantic

admin_router = APIRouter()


class AdminCreate(BaseModel):
    username: str
    password: str


class AdminResponse(BaseModel):
    id: int
    username: str
    remark: Union[str, None] = None
    # create_time: datetime


@admin_router.get("/{admin_id}")
async def admin_pofile(admin_id: int):
    """admin个人信息"""

    query_admin = await Admin.filter(id=admin_id).first()
    if query_admin:
        admin_pydantic = await Admin_Pydantic.from_tortoise_orm(query_admin)
        admin_dict = admin_pydantic.dict(exclude={'password'})
        content = api_result(code=status.HTTP_200_OK, data=jsonable_encoder(admin_dict))
    else:
        content = api_result(code=10002, message=f"管理员用户 {admin_id} 不存在")

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@admin_router.post("/", response_model=Admin_Pydantic)
async def create_admin(admin_data: Admin_Pydantic):
    """新增admin账号"""

    admin_obj = await Admin.create(**admin_data.dict(exclude_unset=True))
    return admin_obj


@router.put("/{admin_id}", response_model=Admin_Pydantic)
async def update_admin(admin_id: int, admin: Admin_Pydantic):
    """更新admin信息"""

    query_admin = await Admin.filter(id=admin_id).first()
    if query_admin:
        pass
        await Admin.filter(id=admin_id).update(**admin.dict(exclude_unset=True))
        updated_admin = await Admin.get(id=admin_id)
    else:
        content = api_result(code=10002, message=f"管理员用户 {admin_id} 不存在")
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@router.delete("/{admin_id}")
async def delete_admin(admin_id: int):
    """删除(禁用)admin"""

    query_admin = await Admin.filter(id=admin_id).first()
    if query_admin:
        pass
        # content = api_result(code=status.HTTP_200_OK, data=jsonable_encoder(admin_dict))
    else:
        content = api_result(code=10002, message=f"管理员用户 {admin_id} 不存在")

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)

    # deleted_count = await Admin.filter(id=admin_id).delete()
    # if not deleted_count:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="管理员不存在")
    # return {"message": "管理员删除成功"}

# @admin_router.post("/", response_model=AdminResponse)
# async def login_test(admin_data: AdminCreate):
#     # 直接创建
#     # admin_obj = await Admin.create(
#     #     username=admin_data.username,
#     #     password=admin_data
#     # )
#
#     # 创建 Admin 对象
#     admin_obj = Admin(username=admin_data.username)
#
#     # 使用 set_password 方法对密码进行加密
#     await admin_obj.set_password(admin_data.password)
#
#     # 保存到数据库
#     await admin_obj.save()
#
#     # 返回创建的 admin 对象
#     print(admin_obj)
#     return admin_obj
