from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime, SmallInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Order(Base):
    __tablename__ = "order_main"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    pay_status = Column(SmallInteger, default=0)  # 0未支付/1已支付/2退款
    pay_time = Column(DateTime, nullable=True)
    order_status = Column(SmallInteger, default=1)  # 1待支付/2已支付/3已完成/4已取消/5超时取消
    pay_type = Column(SmallInteger, nullable=True)  # 1微信支付
    transaction_id = Column(String(64), nullable=True)
    address = Column(Text, nullable=False)
    phone = Column(String(20), nullable=False)
    consignee = Column(String(50), nullable=False)
    remark = Column(Text, nullable=True)
    create_time = Column(DateTime, default=func.now(), index=True)
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())
    expire_time = Column(DateTime, nullable=False, index=True)  # 订单过期时间
    region_id = Column(Integer, nullable=True)  # 地区ID
    
    # 关系定义
    items = relationship("OrderItem", backref="order", lazy="select")

class OrderItem(Base):
    __tablename__ = "order_item"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("order_main.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Numeric(10, 2), nullable=False)
    create_time = Column(DateTime, default=func.now())
