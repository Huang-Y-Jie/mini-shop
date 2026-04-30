from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import verify_user_token
from app.core.redis import get_redis
from app.models import Cart, Product, User

router = APIRouter()

"""
购物车相关API

包括添加商品到购物车、获取购物车列表、更新购物车商品数量、删除购物车商品等功能
"""

class CartAdd(BaseModel):
    product_id: int
    quantity: int = 1

class CartUpdate(BaseModel):
    product_id: int
    quantity: int

@router.post("/add")
async def add_to_cart(cart_data: CartAdd, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    product_id = cart_data.product_id
    quantity = cart_data.quantity
    if not product_id:
        raise HTTPException(status_code=400, detail="缺少商品ID")
    """添加商品到购物车
    
    Args:
        product_id: 商品ID
        quantity: 商品数量，默认1
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 添加结果
        
    Raises:
        HTTPException: 商品不存在或已下架时抛出404异常
    """
    # 检查商品是否存在
    product = db.query(Product).filter(Product.id == product_id, Product.status == 1).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在或已下架")
    
    # 获取或创建购物车
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id, items='[]')
        db.add(cart)
        db.flush()
    
    # 解析购物车商品项
    items = json.loads(cart.items)
    
    # 检查是否已有该商品
    product_exists = False
    for item in items:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            product_exists = True
            break
    
    # 添加新商品
    if not product_exists:
        items.append({'product_id': product_id, 'quantity': quantity})
    
    # 更新购物车
    cart.items = json.dumps(items)
    db.commit()
    
    # 更新Redis缓存
    redis = get_redis()
    if redis:
        redis.set(f"cart:{current_user.id}", cart.items, ex=7*24*60*60)  # 7天过期
    
    return {"code": 200, "msg": "添加成功", "data": None}

@router.get("/items")
async def get_cart_list(current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """获取购物车列表
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 购物车商品列表
    """
    # 先从Redis获取购物车数据
    redis = get_redis()
    cart_data = redis.get(f"cart:{current_user.id}") if redis else None
    
    # 如果Redis中没有，从数据库获取
    if not cart_data:
        cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
        if not cart:
            return {"code": 200, "msg": "success", "data": {"items": []}}
        cart_data = cart.items
        # 更新Redis缓存
        if redis:
            redis.set(f"cart:{current_user.id}", cart_data, ex=7*24*60*60)
    
    # 解析购物车商品项
    items = json.loads(cart_data)
    
    # 过滤已下架或删除的商品
    valid_items = []
    for item in items:
        product = db.query(Product).filter(Product.id == item['product_id'], Product.status == 1).first()
        if product:
            # 添加商品信息
            item_with_info = item.copy()
            item_with_info['product_name'] = product.name
            item_with_info['product_price'] = float(product.price)
            item_with_info['product_images'] = product.cover_img
            item_with_info['amount'] = float(product.price) * item['quantity']
            valid_items.append(item_with_info)
    
    # 如果有无效商品，更新购物车
    if len(valid_items) != len(items):
        cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
        if cart:
            # 只保存product_id和quantity到数据库
            simple_items = [{'product_id': item['product_id'], 'quantity': item['quantity']} for item in valid_items]
            cart.items = json.dumps(simple_items)
            db.commit()
            # 更新Redis缓存
            if redis:
                redis.set(f"cart:{current_user.id}", cart.items, ex=7*24*60*60)
    
    return {"code": 200, "msg": "success", "data": {"items": valid_items}}

@router.put("/items")
async def update_cart_item(cart_data: CartUpdate, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    product_id = cart_data.product_id
    quantity = cart_data.quantity
    if not product_id or not quantity:
        raise HTTPException(status_code=400, detail="缺少必要参数")
    """更新购物车商品数量
    
    Args:
        product_id: 商品ID
        quantity: 新的商品数量
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 更新结果
        
    Raises:
        HTTPException: 商品不存在或已下架时抛出404异常
        HTTPException: 购物车不存在时抛出404异常
        HTTPException: 购物车中不存在该商品时抛出404异常
    """
    # 检查商品是否存在
    product = db.query(Product).filter(Product.id == product_id, Product.status == 1).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在或已下架")
    
    # 获取购物车
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")
    
    # 解析购物车商品项
    items = json.loads(cart.items)
    
    # 查找并更新商品
    product_found = False
    for item in items:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            product_found = True
            break
    
    if not product_found:
        raise HTTPException(status_code=404, detail="购物车中不存在该商品")
    
    # 更新购物车
    cart.items = json.dumps(items)
    db.commit()
    
    # 更新Redis缓存
    redis = get_redis()
    if redis:
        redis.set(f"cart:{current_user.id}", cart.items, ex=7*24*60*60)
    
    return {"code": 200, "msg": "修改成功", "data": None}

@router.delete("/items/{product_id}")
async def delete_cart_item(product_id: int, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """删除购物车商品
    
    Args:
        product_id: 商品ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 删除结果
        
    Raises:
        HTTPException: 购物车不存在时抛出404异常
    """
    # 获取购物车
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="购物车不存在")
    
    # 解析购物车商品项
    items = json.loads(cart.items)
    
    # 过滤掉要删除的商品
    new_items = [item for item in items if item['product_id'] != product_id]
    
    # 更新购物车
    cart.items = json.dumps(new_items)
    db.commit()
    
    # 更新Redis缓存
    redis = get_redis()
    if redis:
        redis.set(f"cart:{current_user.id}", cart.items, ex=7*24*60*60)
    
    return {"code": 200, "msg": "删除成功", "data": None}

@router.delete("/clear")
async def clear_cart(current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """清空购物车
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 清空结果
    """
    # 获取购物车
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        cart.items = '[]'
        db.commit()
        
        # 更新Redis缓存
        redis = get_redis()
        if redis:
            redis.set(f"cart:{current_user.id}", '[]', ex=7*24*60*60)
    
    return {"code": 200, "msg": "清空成功", "data": None}
