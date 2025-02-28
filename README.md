# FastApi_BestPractices

## FastApi 最佳实践

- 如果你是从`Flask` https://github.com/yangyuexiong/Flask_BestPractices 转过来，先了解以下知识点。
    - 异步编程，协程，IO多路复用等相关知识
    - FastApi官方文档：https://fastapi.tiangolo.com/zh/

## 一、安装

- Python3.12+
- pip3
- pipenv

  ```shell script
  pip3 install pipenv
  ```

## 二、配置虚拟环境

- 进入项目根目录

  ```shell script
  cd /FastApi_BestPractices
  ```

- 修改 pipenv 的 pip 安装源(科学上网(翻墙)的同学可以忽略)

    - [Pipfile](./Pipfile)

  ```
  Pipfile 文件修改如下:

  # 国内pip安装源(不能翻墙的同学修改如下,在可以翻墙的情况下依旧国内pip源比较快)
  url = "https://pypi.doubanio.com/simple"

  # 国外pip安装源(可以翻墙)
  url = "https://pypi.org/simple"

  # 修改对应的 Python 版本
  [requires]
  python_version = "3.12"
  ```

- 安装虚拟环境与依赖的包

  ```shell script
  pipenv install
  ```

- 进入虚拟环境

  ```shell script
  pipenv shell
  ```
- `PyCharm`等配置请查阅(`Flask最佳实践`: https://github.com/yangyuexiong/Flask_BestPractices -> `二、配置虚拟环境`)

## 三、配置文件

- 前置准备(如:创建数据库)

    - [/config/dev.ini](./config/dev.ini)
    - [/config/pro.ini](./config/pro.ini)

## 四、ORM

- [db.py](./db.py)
- [db_connect.py](./utils/db_connect.py) 新的的模型需要在`models_list`中添加,例如`app.models.aps_task.models`

  ```shell script
  # 进入项目根目录
  # 进入项目虚拟环境
  pipenv shell
  ```

  ```shell
  # 数据库初始化 
  aerich init -t db.TORTOISE_CONFIG
  aerich init-db
  ```

  ```shell
  # 新增表迁移命令 `--name 描述` 
  aerich migrate --name message
  aerich upgrade
  ```

## 五、路由注册

- 创建(路由,Api,视图)

    - [增删改查](./app/api/admin_api/admin_api.py)

- 路由注册

    - [/FastApi_BestPractices/app/api/**init**.py](./app/api/__init__.py)

## 六、钩子函数(拦截器):

- 中间件`class MyMiddleware` 注册在app实例中

    - [ApplicationExample.py](./ApplicationExample.py)

## 七、自定义异常:

- [api_result.py](./common/libs/api_result.py) 在`custom_http_dict`按照例子添加

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

- 定时任务: [task_handler](./utils/scheduled_tasks/task_handler.py)

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

- 代码中可能存在大量打印调试代码语句`print('xxxx')`可以将其注释或者删除。

- 快试试快速实现你业务需求吧！！！嘻嘻！！！