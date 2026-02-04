# -*- coding: utf-8 -*-
# @Time    : 2024/8/26 13:42
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : task_handler.py
# @Software: PyCharm

import pytz
from enum import Enum
from datetime import datetime

from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import ConflictingIdError

from app.models.aps_task import ApsTask
from app.tasks import tasks as TaskDict

scheduler = AsyncIOScheduler()


class TriggerType(str, Enum):
    date = "date"
    interval = "interval"
    cron = "cron"


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

    def date_trigger(self):
        """DateTrigger"""

        if not self.trigger_time:
            raise TypeError("DateTrigger 缺少 trigger_time")

        run_date = datetime.strptime(self.trigger_time, "%Y-%m-%d %H:%M:%S")
        run_date = self.trigger_time
        trigger = DateTrigger(run_date=run_date, timezone=self.timezone)
        self.trigger_param = {
            "trigger_time": run_date
        }
        return trigger

    def interval_trigger(self):
        """IntervalTrigger"""

        if not isinstance(self.interval_kw, dict):
            raise TypeError("IntervalTrigger 参数 interval_kw 错误")

        trigger = IntervalTrigger(timezone=self.timezone, **self.interval_kw)
        self.trigger_param = {
            "interval_kw": self.interval_kw
        }
        return trigger

    def cron_trigger(self):
        """CronTrigger"""

        if not self.cron_expression:
            raise TypeError("CronTrigger 缺少 cron_expression")

        trigger = CronTrigger.from_crontab(expr=self.cron_expression, timezone=self.timezone)
        self.trigger_param = {
            "cron_expression": self.cron_expression
        }
        return trigger

    def get_trigger(self):
        """获取触发器"""

        trigger_dict = {
            "date": self.date_trigger,
            "interval": self.interval_trigger,
            "cron": self.cron_trigger
        }
        self.trigger = trigger_dict.get(self.trigger_type)()
        return self.trigger

    def get_task_function(self):
        """获取任务函数"""

        if self.skip_function_check:
            return self.task_function

        if hasattr(TaskDict, self.task_function_name):
            self.task_function = getattr(TaskDict, self.task_function_name)
            return self.task_function
        else:
            raise AttributeError(f"任务函数 '{self.task_function_name}' 不存在")


class TaskHandler(TriggerHandler):
    """定时任务处理器"""

    def add_task(self):
        """新增定时任务"""

        self.get_trigger()  # -> self.trigger
        self.get_task_function()  # -> self.task_function

        try:
            scheduler.add_job(
                self.task_function,
                trigger=self.trigger,
                id=self.task_id,
                args=self.task_function_args,
                kwargs=self.task_function_kwargs
            )
            return True, f"定时任务: {self.task_id} 新增成功"
        except ConflictingIdError as e:
            return False, f"定时任务: {self.task_id} 已存在: {e}"

    def update_task(self):
        """更新定时任务"""

        remove_result, remove_message = self.remove_task(task_id=self.task_id)
        add_result, add_message = self.add_task()

        if not remove_result or not add_result:
            return False, f"定时任务: {self.task_id} 更新失败"
        else:
            return True, f"定时任务: {self.task_id} 更新成功"

    @classmethod
    def remove_task(cls, task_id):
        """删除定时任务"""

        if scheduler.get_job(task_id):
            scheduler.remove_job(task_id)
            return True, f"定时任务: {task_id} 删除成功"
        else:
            return False, f"定时任务: {task_id} 不存在"

    @classmethod
    def get_task_state(cls, task_id):
        """定时任务详情"""

        job = scheduler.get_job(task_id)
        if job:
            res = {
                "id": job.id,
                "next_run_time": job.next_run_time
            }
            return res
        else:
            return {}

    @staticmethod
    def get_all_task_states():
        """定时任务列表"""

        all_jobs = scheduler.get_jobs()
        task_states = []
        for job in all_jobs:
            d = {
                "id": job.id,
                "next_run_time": job.next_run_time
            }
            task_states.append(d)
        return task_states


async def scheduler_init():
    """初始化定时任务"""

    tasks = await ApsTask.filter(is_deleted=0).all()

    for task in tasks:
        task_id = task.task_id
        trigger_type = task.trigger_type
        trigger_param: dict = task.trigger_param
        task_function_name = task.task_function_name
        task_function_args = task.task_function_args
        task_function_kwargs = task.task_function_kwargs

        if trigger_param:
            task_handler = TaskHandler(
                task_id=task_id,
                trigger_type=trigger_type,
                # trigger_time=request_data.trigger_time,
                # interval_kw=request_data.interval_kw,
                # cron_expression=request_data.cron_expression,
                task_function_name=task_function_name,
                task_function_args=task_function_args,
                task_function_kwargs=task_function_kwargs
            )

            for k, v in trigger_param.items():
                setattr(task_handler, k, v)

            task_handler.add_task()

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

    test2 = TaskHandler(
        task_id=TaskDict.test_async_task.__name__,
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
        task_function_name=TaskDict.test_async_task.__name__
    )
    result, message = test2.add_task()
    print(result, message)

    scheduler.start()
