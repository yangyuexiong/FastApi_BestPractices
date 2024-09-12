# -*- coding: utf-8 -*-
# @Time    : 2024/7/24 21:28
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : all_reference.py
# @Software: PyCharm

from datetime import datetime, timedelta
from enum import Enum
from typing import Union, List, Annotated

import shortuuid
from fastapi import (
    APIRouter, Depends, Request, Header, Path, Body, Query, Cookie, status, HTTPException, Form, UploadFile, File,
    BackgroundTasks
)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field

import utils.redis_connect as rp
from utils.redis_connect import get_value, set_key_value, delete_value
from common.libs.custom_exception import CustomException
from common.libs.common_pydantic_base import CommonPydanticCreate, CommonPydanticUpdate
from common.libs.common_page import CommonPage, page_size, query_result
from common.libs.common_select import select
from common.libs.auth import Token, get_token_header, check_admin_existence
from common.libs.api_result import api_response
from common.libs.common_paginate_query import cpq
