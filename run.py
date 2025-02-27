# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 14:28
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : run.py
# @Software: PyCharm


import uvicorn

from ApplicationExample import create_app

app = create_app()

if __name__ == '__main__':
    # uvicorn.run(app, host="0.0.0.0", port=9999)
    uvicorn.run("run:app", host="0.0.0.0", port=7769, reload=True)
