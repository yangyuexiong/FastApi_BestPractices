# -*- coding: utf-8 -*-
# @Time    : 2024/4/13 18:47
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : all_reference.py
# @Software: PyCharm

from datetime import datetime
from typing import Union, List, Annotated

from fastapi import APIRouter, Depends, Header, Query, Cookie, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict

from common.libs.common_page import CommonPage, page_size
from common.libs.api_result import api_result
