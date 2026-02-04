# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 15:34
# @Author  : yangyuexiong
# @Email   : yang6333yyx@126.com
# @File    : config.py
# @Software: PyCharm

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ENV = "development"
ENV_FILE_ENV_VAR = "ENV_FILE"


def normalize_env(env: Optional[str]) -> str:
    value = (env or "").strip().lower()
    mapping = {
        "dev": "development",
        "development": "development",
        "test": "test",
        "testing": "test",
        "prod": "production",
        "production": "production",
        "stage": "staging",
        "staging": "staging",
    }
    return mapping.get(value, value or DEFAULT_ENV)


ENV_FILE_MAP = {
    "development": ".env.development",
    "test": ".env.test",
    "production": ".env.production",
    "staging": ".env.staging",
}


def resolve_env_files(env_name: str) -> List[Path]:
    if env_name not in ENV_FILE_MAP:
        raise ValueError(f"Unsupported ENV: {env_name}")

    paths: List[Path] = []

    explicit = os.getenv(ENV_FILE_ENV_VAR)
    if explicit:
        explicit_path = Path(explicit)
        if not explicit_path.is_absolute():
            explicit_path = BASE_DIR / explicit_path
        if explicit_path.exists():
            paths.append(explicit_path)
        else:
            raise FileNotFoundError(f"{ENV_FILE_ENV_VAR} 指定的文件不存在: {explicit_path}")

    base_env = BASE_DIR / ".env"
    if base_env.exists():
        paths.append(base_env)

    env_specific = BASE_DIR / ENV_FILE_MAP[env_name]
    if env_specific.exists():
        paths.append(env_specific)

    if paths:
        return paths

    raise FileNotFoundError(
        f"未找到配置文件，请创建 {ENV_FILE_MAP.get(env_name)} 或设置 {ENV_FILE_ENV_VAR}"
    )


"""
extra = 'allow' ✅
允许额外的字段（不在模型定义中的字段）

extra = 'ignore' ⚠️
忽略额外的字段

extra = 'forbid' ❌
禁止额外的字段
"""

BASE_SETTINGS_CONFIG = SettingsConfigDict(
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="ignore",
)


class BaseConfig(BaseSettings):
    """配置基类"""

    model_config = BASE_SETTINGS_CONFIG

    # 基础配置
    APP_NAME: str = "yangyuexiong"
    ENV: str
    SECRET_KEY: str
    DEBUG: bool
    RUN_HOST: str
    RUN_PORT: int

    # MySQL配置
    MYSQL_HOSTNAME: str
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str
    MYSQL_PORT: int
    MYSQL_DATABASE: str

    # POSTGRESQL配置
    POSTGRESQL_HOSTNAME: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_PORT: int
    POSTGRESQL_DATABASE: str

    # Redis配置
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PWD: str
    REDIS_DB: int
    DECODE_RESPONSES: bool

    # 日志脱敏配置
    SENSITIVE_HEADERS: str = "authorization,cookie,set-cookie,x-api-key"

    @property
    def ENV_NAME(self) -> str:
        return normalize_env(self.ENV)

    @property
    def IS_DEV(self) -> bool:
        return self.ENV_NAME == "development"

    @property
    def IS_TEST(self) -> bool:
        return self.ENV_NAME == "test"

    @property
    def IS_PROD(self) -> bool:
        return self.ENV_NAME == "production"

    @property
    def IS_STAGING(self) -> bool:
        return self.ENV_NAME == "staging"

    @property
    def MASK_SENSITIVE_HEADERS(self) -> bool:
        # 生产与预发布默认脱敏；如需调整可在此修改策略
        return self.IS_PROD or self.IS_STAGING

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.REDIS_PWD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}?decode_responses={self.DECODE_RESPONSES}"

    @property
    def mysql_url(self) -> str:
        return "mysql://{}:{}@{}:{}/{}".format(
            self.MYSQL_USERNAME,
            self.MYSQL_PASSWORD,
            self.MYSQL_HOSTNAME,
            self.MYSQL_PORT,
            self.MYSQL_DATABASE
        )

    @property
    def pg_url(self) -> str:
        return "postgres://{}:{}@{}:{}/{}".format(
            self.POSTGRESQL_USERNAME,
            self.POSTGRESQL_PASSWORD,
            self.POSTGRESQL_HOSTNAME,
            self.POSTGRESQL_PORT,
            self.POSTGRESQL_DATABASE
        )


@lru_cache
def get_config(env: Optional[str] = None) -> BaseConfig:
    """获取配置文件"""

    fast_api_env = normalize_env(env or os.getenv("FAST_API_ENV", DEFAULT_ENV))
    env_files = resolve_env_files(fast_api_env)
    logger.info(f"加载配置: env={fast_api_env}, files={[str(p) for p in env_files]}")
    conf = BaseConfig(_env_file=[str(p) for p in env_files])
    if conf.ENV_NAME != fast_api_env:
        logger.warning(f"ENV 不一致：FAST_API_ENV={fast_api_env}, 配置 ENV={conf.ENV_NAME}")
    return conf


if __name__ == '__main__':
    dev_config = get_config("development")
    print(dev_config.model_dump())
    print(dev_config.APP_NAME)
    print(dev_config.MYSQL_HOSTNAME)

    pro_config = get_config("production")
    print(pro_config.model_dump())
