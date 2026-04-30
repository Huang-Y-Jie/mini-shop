from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import verify_user_token
from app.core.redis import get_redis
from app.core.logger import log_action
from app.models import User, Address
from pydantic import BaseModel
from typing import List

router = APIRouter()

class AddressCreate(BaseModel):
    name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool = False

class AddressUpdate(BaseModel):
    name: str = None
    phone: str = None
    province: str = None
    city: str = None
    district: str = None
    detail: str = None
    is_default: bool = None

class AddressResponse(BaseModel):
    id: int
    name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool
    
    class Config:
        from_attributes = True

@router.post("/")
async def create_address(address: AddressCreate, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """创建新地址"""
    try:
        # 如果设置为默认地址，先将其他地址设为非默认
        if address.is_default:
            db.query(Address).filter(Address.user_id == current_user.id, Address.is_default == True).update({"is_default": False})
        
        # 创建新地址
        new_address = Address(
            user_id=current_user.id,
            name=address.name,
            phone=address.phone,
            province=address.province,
            city=address.city,
            district=address.district,
            detail=address.detail,
            is_default=address.is_default
        )
        
        db.add(new_address)
        db.commit()
        db.refresh(new_address)
        
        # 清除缓存
        redis = get_redis()
        if redis:
            redis.delete(f"user:{current_user.id}:addresses")
        
        log_action("address", str(current_user.id), "create", "success", f"地址ID: {new_address.id}")
        return {"code": 200, "msg": "success", "data": {
            "id": new_address.id,
            "name": new_address.name,
            "phone": new_address.phone,
            "province": new_address.province,
            "city": new_address.city,
            "district": new_address.district,
            "detail": new_address.detail,
            "is_default": new_address.is_default
        }}
    except Exception as e:
        log_action("address", str(current_user.id), "create", "fail", str(e))
        return {"code": 500, "msg": "创建地址失败", "data": None}

@router.get("/")
async def get_addresses(current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """获取用户所有地址"""
    try:
        # 从数据库获取
        addresses = db.query(Address).filter(Address.user_id == current_user.id).order_by(Address.is_default.desc(), Address.update_time.desc()).all()
        
        # 构造返回数据
        result = []
        for addr in addresses:
            result.append({
                "id": addr.id,
                "name": addr.name,
                "phone": addr.phone,
                "province": addr.province,
                "city": addr.city,
                "district": addr.district,
                "detail": addr.detail,
                "is_default": addr.is_default
            })
        
        return {"code": 200, "msg": "success", "data": result}
    except Exception as e:
        log_action("address", str(current_user.id), "get", "fail", str(e))
        return {"code": 500, "msg": "获取地址失败", "data": []}

@router.get("/{address_id}")
async def get_address(address_id: int, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """获取单个地址详情"""
    try:
        address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
        if not address:
            return {"code": 404, "msg": "地址不存在", "data": None}
        return {"code": 200, "msg": "success", "data": {
            "id": address.id,
            "name": address.name,
            "phone": address.phone,
            "province": address.province,
            "city": address.city,
            "district": address.district,
            "detail": address.detail,
            "is_default": address.is_default
        }}
    except Exception as e:
        log_action("address", str(current_user.id), "get_detail", "fail", str(e))
        return {"code": 500, "msg": "获取地址详情失败", "data": None}

@router.put("/{address_id}")
async def update_address(address_id: int, address: AddressUpdate, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """更新地址"""
    try:
        # 查找地址
        existing_address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
        if not existing_address:
            return {"code": 404, "msg": "地址不存在", "data": None}
        
        # 如果设置为默认地址，先将其他地址设为非默认
        if address.is_default:
            db.query(Address).filter(Address.user_id == current_user.id, Address.is_default == True).update({"is_default": False})
        
        # 更新地址信息
        update_data = address.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing_address, field, value)
        
        db.commit()
        db.refresh(existing_address)
        
        # 清除缓存
        redis = get_redis()
        if redis:
            redis.delete(f"user:{current_user.id}:addresses")
        
        log_action("address", str(current_user.id), "update", "success", f"地址ID: {address_id}")
        return {"code": 200, "msg": "success", "data": {
            "id": existing_address.id,
            "name": existing_address.name,
            "phone": existing_address.phone,
            "province": existing_address.province,
            "city": existing_address.city,
            "district": existing_address.district,
            "detail": existing_address.detail,
            "is_default": existing_address.is_default
        }}
    except Exception as e:
        log_action("address", str(current_user.id), "update", "fail", str(e))
        return {"code": 500, "msg": "更新地址失败", "data": None}

@router.delete("/{address_id}")
async def delete_address(address_id: int, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """删除地址"""
    try:
        # 查找地址
        address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
        if not address:
            raise HTTPException(status_code=404, detail="地址不存在")
        
        db.delete(address)
        db.commit()
        
        # 清除缓存
        redis = get_redis()
        if redis:
            redis.delete(f"user:{current_user.id}:addresses")
        
        log_action("address", str(current_user.id), "delete", "success", f"地址ID: {address_id}")
        return {"code": 200, "msg": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        log_action("address", str(current_user.id), "delete", "fail", str(e))
        raise HTTPException(status_code=500, detail="删除地址失败")
