import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "mysql://root:mysql@localhost:3308/shop"
    
    # Redis配置
    REDIS_URL: str = "redis://10.16.18.70:6379/0"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # 微信支付配置
    WX_APPID: str = "your-wx-appid"
    WX_APPSECRET: str = "your-wx-appsecret"
    WX_MCHID: str = "your-wx-mchid"
    WX_API_KEY: str = "your-wx-api-key"
    WX_NOTIFY_URL: str = "http://localhost:8000/api/pay/callback"
    
    # 图片存储配置
    IMAGE_STORAGE_TYPE: str = "local"  # local 或 cloud
    IMAGE_LOCAL_PATH: str = "./uploads"
    IMAGE_BASE_URL: str = "http://localhost:8002/uploads"
    
    # 其他配置
    ORDER_TIMEOUT_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()