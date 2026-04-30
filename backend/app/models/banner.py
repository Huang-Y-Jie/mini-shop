from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime

class Banner(Base):
    __tablename__ = "banner"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, comment='轮播图标题')
    subtitle = Column(String(255), nullable=False, comment='轮播图副标题')
    image = Column(Text, nullable=False, comment='轮播图图片URL')
    link = Column(String(500), nullable=True, comment='轮播图链接')
    sort = Column(Integer, default=0, comment='排序')
    status = Column(Boolean, default=True, comment='状态')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'image': self.image,
            'link': self.link,
            'sort': self.sort,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
