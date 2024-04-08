# -*- coding: utf-8 -*-
# @Time    : 2024/4/5 17:46
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : run.py
# @Software: PyCharm

from ApplicationExample import create_app

app = create_app()

if __name__ == '__main__':
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=9999)
    uvicorn.run("run:app", host="0.0.0.0", port=9999, reload=True)
    # uvicorn.run("run:app", host="192.168.50.149", port=9999, reload=True)
