from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Cart(Base):
    __tablename__ = "cart"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True, index=True)
    items = Column(Text, nullable=False, default='[]')  # JSON数组格式存储商品项
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())
