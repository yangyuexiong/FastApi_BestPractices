FROM python:3.12-slim

MAINTAINER YangYueXiong

# 更新pip
RUN pip install --upgrade pip -i https://pypi.doubanio.com/simple

# 安装pipenv
RUN pip install pipenv -i https://pypi.doubanio.com/simple

# 复制应用程序代码
WORKDIR /srv
COPY . /srv/FastApi_BestPractices

# 设置工作目录为
WORKDIR /srv/FastApi_BestPractices

# 安装项目依赖包
# --system标志，因此它会将所有软件包安装到系统 python 中，而不是安装到virtualenv. 由于docker容器不需要有virtualenvs
# --deploy标志，因此如果您的版本Pipfile.lock已过期，您的构建将失败
# --ignore-pipfile，所以它不会干扰我们的设置
RUN pipenv install --system --deploy --ignore-pipfile

# 设置环境变量
ENV FAST_API_ENV=production

# 时区
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 启动 FastAPI 应用
#CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD python project_init.py && uvicorn run:app --host 0.0.0.0 --port 8000
#CMD uvicorn run:app --host 0.0.0.0 --port 8000
CMD ["sh", "-c", "python project_init.py && uvicorn run:app --host 0.0.0.0 --port 8000"]


# 暴露 FastAPI 的默认端口
EXPOSE 8000