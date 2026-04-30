from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 使用pymysql作为驱动（仅当数据库是MySQL时）
if settings.DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = settings.DATABASE_URL.replace("mysql://", "mysql+pymysql://")
    # 添加字符集配置，使用utf8而不是utf8mb4
    DATABASE_URL += "?charset=utf8"
else:
    DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()