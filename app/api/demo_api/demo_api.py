# -*- coding: utf-8 -*-
# @Time    : 2024/4/17 15:57
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : demo_api.py
# @Software: PyCharm


from all_reference import *

demo_router = APIRouter(
    dependencies=[Depends(get_token_header)]
)


class DemoReqBody(BaseModel):
    """登录请求体参数与类型"""

    username: str
    password: str
    title: str = "okc"
    login_type: Union[str, int, None] = None


class DemoOut(BaseModel):
    """响应模型"""

    username: str
    title: str
    age: int = 666
    login_type: Union[str, int, None] = None
    tags: list = []


class Message(BaseModel):
    message: str


"""
response_model_exclude_unset:
    只返回`response_model`中有值的字段:   response_model_exclude_unset=True

response_model_include:
    只返回`response_model`中需要的字段:   {"username", "title", ...}

response_model_exclude:
    去掉`response_model`中不需要的字段:   {"username", "title", ...}

"""

"""
局部拦截器:
    dependencies=[Depends(verify_token), Depends(verify_key)]

"""


@demo_router.post(
    "/demo",
    dependencies=[Depends(get_token_header)],
    response_model=DemoOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": Message, "description": "The item was not found"},
        200: {
            "description": "Item requested by ID",
            "content": {
                "application/json": {
                    "example": {"id": "bar", "value": "The bar tenders"}
                }
            },
        },
    },
)
# @demo_router.post("/", response_model=DemoOut, response_model_exclude_unset=True)
# @demo_router.post("/", response_model=DemoOut, response_model_include={"username", "title"})
# @demo_router.post("/", response_model=DemoOut, response_model_exclude={"username", "title"})
async def demo(data: DemoReqBody, user_info: dict = Depends(get_token_header)):
    """demo"""

    print(data.username)
    print(data.password)
    print(data)
    print(jsonable_encoder(data))
    # print(1 / 0)
    # raise CustomException(status_code=400, detail="自定义异常", custom_code=100001, data=[1, 2, 3])
    # return data

    headers = {
        "add-demo-header-key": "add-demo-header-value"
    }
    content = api_result(code=status.HTTP_200_OK, message="登录成功", data=jsonable_encoder(data))
    response = JSONResponse(status_code=status.HTTP_200_OK, content=content, headers=headers)
    response.set_cookie(key="add-demo-session", value="demo-cookie-session-value")
    return response
