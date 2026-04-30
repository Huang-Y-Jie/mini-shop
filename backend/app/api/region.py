from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import verify_user_token
from app.core.redis import get_redis
from app.models import RegionShipping, User
import json

router = APIRouter()

class RegionShippingCreate(BaseModel):
    region_name: str
    shipping_fee: float
    is_active: int = 1

class RegionShippingUpdate(BaseModel):
    region_name: str = None
    shipping_fee: float = None
    is_active: int = None

@router.get("/list")
async def get_region_list(is_active: int = None, db: Session = Depends(get_db)):
    """获取地区运费列表
    
    Args:
        is_active: 是否启用，可选
        db: 数据库会话
        
    Returns:
        dict: 地区运费列表
    """
    # 构建缓存键
    cache_key = f"region:list:{is_active or 'all'}"
    
    # 尝试从Redis获取
    redis = get_redis()
    if redis:
        cached_data = redis.get(cache_key)
        if cached_data:
            return {"code": 200, "msg": "success", "data": json.loads(cached_data)}
    
    # 从数据库获取
    query = db.query(RegionShipping)
    
    if is_active is not None:
        query = query.filter(RegionShipping.is_active == is_active)
    
    regions = query.order_by(RegionShipping.id).all()
    
    region_list = []
    for region in regions:
        region_list.append({
            "id": region.id,
            "region_name": region.region_name,
            "shipping_fee": float(region.shipping_fee),
            "is_active": region.is_active,
            "create_time": region.create_time.isoformat()
        })
    
    # 缓存结果
    if redis:
        redis.set(cache_key, json.dumps(region_list), ex=30*60)  # 30分钟过期
    
    return {"code": 200, "msg": "success", "data": region_list}

@router.post("/")
async def create_region(region_data: RegionShippingCreate, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """添加地区运费
    
    Args:
        region_data: 地区运费数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 操作结果
    """
    # 检查地区名称是否已存在
    existing_region = db.query(RegionShipping).filter(RegionShipping.region_name == region_data.region_name).first()
    if existing_region:
        raise HTTPException(status_code=400, detail="地区名称已存在")
    
    # 创建地区运费
    region = RegionShipping(
        region_name=region_data.region_name,
        shipping_fee=region_data.shipping_fee,
        is_active=region_data.is_active
    )
    db.add(region)
    db.commit()
    db.refresh(region)
    
    # 清除缓存
    redis = get_redis()
    if redis:
        redis.delete("region:list:*")
    
    return {"code": 200, "msg": "添加成功", "data": {"id": region.id}}

@router.put("/{id}")
async def update_region(id: int, region_data: RegionShippingUpdate, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """更新地区运费
    
    Args:
        id: 地区ID
        region_data: 地区运费数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 操作结果
    """
    # 查找地区
    region = db.query(RegionShipping).filter(RegionShipping.id == id).first()
    if not region:
        raise HTTPException(status_code=404, detail="地区不存在")
    
    # 检查地区名称是否已存在
    if region_data.region_name and region_data.region_name != region.region_name:
        existing_region = db.query(RegionShipping).filter(RegionShipping.region_name == region_data.region_name).first()
        if existing_region:
            raise HTTPException(status_code=400, detail="地区名称已存在")
    
    # 更新地区运费
    if region_data.region_name:
        region.region_name = region_data.region_name
    if region_data.shipping_fee is not None:
        region.shipping_fee = region_data.shipping_fee
    if region_data.is_active is not None:
        region.is_active = region_data.is_active
    
    db.commit()
    
    # 清除缓存
    redis = get_redis()
    if redis:
        redis.delete("region:list:*")
    
    return {"code": 200, "msg": "更新成功", "data": None}

@router.delete("/{id}")
async def delete_region(id: int, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """删除地区运费
    
    Args:
        id: 地区ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 操作结果
    """
    # 查找地区
    region = db.query(RegionShipping).filter(RegionShipping.id == id).first()
    if not region:
        raise HTTPException(status_code=404, detail="地区不存在")
    
    # 删除地区运费
    db.delete(region)
    db.commit()
    
    # 清除缓存
    redis = get_redis()
    if redis:
        redis.delete("region:list:*")
    
    return {"code": 200, "msg": "删除成功", "data": None}
