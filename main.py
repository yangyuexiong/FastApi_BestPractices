# -*- coding: utf-8 -*-
# @Time    : 2023/12/29 19:02
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : main.py
# @Software: PyCharm

from ApplicationExample import create_app

app = create_app()

if __name__ == '__main__':
    import uvicorn

    # uvicorn.run(app, host="127.0.0.1", port=8000)

    uvicorn.run("main:app", host="0.0.0.0", port=9999, reload=True)
