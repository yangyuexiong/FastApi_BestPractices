FROM python:3.12-slim

MAINTAINER YangYueXiong

# 更新pip
RUN pip install --upgrade pip -i https://pypi.doubanio.com/simple

# 安装uv
RUN pip install uv -i https://pypi.doubanio.com/simple

# 设置工作目录
WORKDIR /srv/FastApi_BestPractices

# 先复制依赖清单，利用缓存
COPY pyproject.toml /srv/FastApi_BestPractices

# 创建虚拟环境并安装依赖
RUN uv venv
ENV PATH="/srv/FastApi_BestPractices/.venv/bin:$PATH"
RUN uv sync --no-dev

# 复制应用程序代码
COPY . /srv/FastApi_BestPractices

# 设置环境变量
ENV FAST_API_ENV=production

# 时区
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 启动 FastAPI 应用
#CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD python project_init.py && uvicorn run:app --host 0.0.0.0 --port 8000
#CMD uvicorn run:app --host 0.0.0.0 --port 8000
CMD ["sh", "-c", "python scripts/init_project.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]


# 暴露 FastAPI 的默认端口
EXPOSE 8000
