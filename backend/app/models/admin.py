from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from sqlalchemy.sql import func
from app.core.database import Base

class Admin(Base):
    __tablename__ = "admin_user"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False)
    role = Column(SmallInteger, default=1)  # 1=超级管理员
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())