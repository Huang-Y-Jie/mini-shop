from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime, SmallInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "product"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    desc = Column(Text, nullable=True)  # 改为desc
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    cover_img = Column(String(255), nullable=False)
    imgs = Column(Text, nullable=True)  # JSON格式存储多张图片
    sales = Column(Integer, default=0)  # 销售数量
    status = Column(SmallInteger, default=1)  # 1上架/0下架
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联分类
    category = relationship("Category", backref="products")
