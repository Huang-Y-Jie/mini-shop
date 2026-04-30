from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    openid = Column(String(100), unique=True, nullable=False, index=True)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True, unique=True, index=True)
    address = Column(Text, nullable=True)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())