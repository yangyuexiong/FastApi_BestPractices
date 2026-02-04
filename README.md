# FastApi_BestPractices

## FastApi 最佳实践

- 如果你是从`Flask` https://github.com/yangyuexiong/Flask_BestPractices 转过来，先了解以下知识点。
    - 异步编程，协程，IO多路复用等相关知识
    - FastApi官方文档：https://fastapi.tiangolo.com/zh/

## 一、安装

- Python3.12+
- pip3
- uv

  ```shell script
  pip3 install uv
  ```

## 二、配置虚拟环境

- 进入项目根目录

  ```shell script
  cd /Users/yangyuexiong/Desktop/FastApi_BestPractices
  ```

- 可选：配置国内源（不需要翻墙的同学）

  ```shell
  export UV_INDEX_URL=https://pypi.doubanio.com/simple
  ```

- 安装虚拟环境与依赖的包

  ```shell script
  uv venv
  source .venv/bin/activate
  uv lock
  uv sync
  ```
- `PyCharm`等配置请查阅(`Flask最佳实践`: https://github.com/yangyuexiong/Flask_BestPractices -> `二、配置虚拟环境`)

## 三、配置文件

- 前置准备(如:创建数据库)

    - `/.env.development`
    - `/.env.test`
    - `/.env.staging`
    - `/.env.production`

## 项目结构

```
FastApi_BestPractices/
├─ app/
│  ├─ api/                 # 路由与接口
│  │  └─ v1/
│  │     └─ routers/       # 业务路由
│  ├─ core/                # 配置、异常、生命周期、中间件、通用能力
│  ├─ db/                  # 数据库与缓存连接
│  ├─ models/              # ORM 模型
│  ├─ schemas/             # Pydantic 入参/出参模型
│  ├─ tasks/               # 定时任务与调度
│  ├─ utils/               # 通用工具
│  ├─ static/              # 静态资源
│  └─ main.py              # 应用入口
├─ docker/                 # 部署与容器配置
├─ migrations/             # 数据库迁移
├─ scripts/                # 初始化脚本等
├─ tests/                  # 测试
├─ .env.*                  # 多环境配置
├─ Dockerfile
├─ pyproject.toml
└─ README.md
```

## 四、ORM

- [tortoise.py](./app/db/tortoise.py)
- [tortoise.py](./app/db/tortoise.py) 新的模型需要在`models_list`中添加,例如`app.models.aps_task`

  ```shell script
  # 进入项目根目录
  # 进入项目虚拟环境
  source .venv/bin/activate
  ```

  ```shell
  # 数据库初始化 
  aerich init -t app.db.tortoise.TORTOISE_CONFIG
  aerich init-db
  ```

  ```shell
  # 新增表迁移命令 `--name 描述` 
  aerich migrate --name message
  aerich upgrade
  ```

## 五、路由注册

- 创建(路由,Api,视图)

    - [增删改查](./app/api/v1/routers/admin.py)

- 路由注册

    - [app/api/v1/router.py](./app/api/v1/router.py)

## 六、钩子函数(拦截器):

- 中间件`class MyMiddleware` 注册在app实例中

    - [app/main.py](./app/main.py)

## 七、自定义异常:

- [response.py](./app/core/response.py) 在`custom_http_dict`按照例子添加

## 八、任务

- 异步任务

    - 轻量级异步任务(fastapi自带的`BackgroundTasks`)

    ```python
    @app.post("/")
    async def demo(background_tasks: BackgroundTasks):
        
        # 有参数就**task_kw,没有就不传
        background_tasks.add_task(time_task, **task_kw)
        return api_response(data=["dingding"])
  ```

    - celery异步任务:查阅`Flask最佳实践` https://github.com/yangyuexiong/Flask_BestPractices

- 定时任务: [scheduler.py](./app/tasks/scheduler.py)

    ```python
  
    # 代码片段
    class TriggerHandler:
        """TriggerHandler(返回:trigger)"""
    
        def __init__(self, task_id: str, trigger_type: TriggerType, trigger_time: str = None, interval_kw: dict = None,
                     cron_expression: str = None, timezone=pytz.timezone('Asia/Shanghai'), task_function_name: str = None,
                     skip_function_check: bool = False, task_function=None,
                     task_function_args: list = None, task_function_kwargs: dict = None):
    
            self.task_id = task_id  # 任务ID(自定义)
            self.trigger_type = trigger_type  # 触发器类型
            self.trigger = None  # 触发器`get_trigger`返回设值
            self.trigger_param = {}  # 触发器`get_trigger`设值用户写入数据库字段,随后通过`**kwargs`传递给`trigger`
            self.trigger_time = trigger_time  # 使用`DateTrigger`必须的参数 例:`2024-05-20 13:14:00`
            self.interval_kw = interval_kw  # 使用`IntervalTrigger`必须的参数
            self.cron_expression = cron_expression  # 使用`CronTrigger`必须的参数 例: `0 15 10 * *`
            self.timezone = timezone  # 时区默认中国
            self.task_function_name = task_function_name  # 定时任务函数名称
            self.skip_function_check = skip_function_check  # 忽略函数检查跳过`self.get_task_function()`的逻辑,直接使用构造函数的`task_function`
            self.task_function = task_function  # 任务函数`get_task_function`返回设值
            self.task_function_args = task_function_args  # 定时任务函数args参数
            self.task_function_kwargs = task_function_kwargs  # 定时任务函数kwargs参数
    ```

    - 间隔触发任务(在`scheduler_init`中注册)

    ```python
  # 使用 interval_kw
  async def scheduler_init():
      """初始化定时任务"""
  
      ...
          
      test1 = TaskHandler(
          task_id=TaskDict.test_sync_task.__name__,
          trigger_type=TriggerType.interval,
          interval_kw={
              "weeks": 0,
              "days": 0,
              "hours": 0,
              "minutes": 0,
              "seconds": 5,
              "start_date": None,
              "end_date": None
          },
          task_function_name=TaskDict.test_sync_task.__name__
      )
      result, message = test1.add_task()
      print(result, message)
  
      ...
    ```

    - 日期触发任务
    ```python
  # 使用 date
  async def scheduler_init():
      """初始化定时任务"""
  
      ...
          
      test1 = TaskHandler(
          task_id=TaskDict.test_sync_task.__name__,
          trigger_type=TriggerType.date,
          trigger_time="2024-05-20 13:14:00",
          task_function_name=TaskDict.test_sync_task.__name__
      )
      result, message = test1.add_task()
      print(result, message)
  
      ...
    ```

    - 日期触发任务
    ```python
  # 使用 cron
  async def scheduler_init():
      """初始化定时任务"""
  
      ...
          
      test1 = TaskHandler(
          task_id=TaskDict.test_sync_task.__name__,
          trigger_type=TriggerType.cron,
          cron_expression="0 15 10 * *",
          task_function_name=TaskDict.test_sync_task.__name__
      )
      result, message = test1.add_task()
      print(result, message)
  
      ...
    ```

## 九、部署

  ```shell
     docker compose -p FastApi_BestPractices up -d
  ```

## 备注

- 建议通过 `FAST_API_ENV=development|test|staging|production` 选择环境
- 配置文件使用 `/.env.*`，可参考 `/.env.example`
