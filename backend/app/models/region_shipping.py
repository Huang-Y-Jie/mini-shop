from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.core.database import Base

class RegionShipping(Base):
    __tablename__ = "region_shipping"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    region_name = Column(String(100), nullable=False, comment="地区名称")
    shipping_fee = Column(Float, nullable=False, comment="运费")
    is_active = Column(Integer, default=1, comment="是否启用: 1=启用, 0=禁用")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")