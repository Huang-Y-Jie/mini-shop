from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import os
import uuid
from app.core.database import get_db
from app.core.auth import create_admin_token, verify_admin_token, verify_password
from app.core.redis import get_redis
from app.core.bloom_filter import product_bloom_filter
from app.models import Admin, Product, Category, Order, OrderItem, User, Cart

router = APIRouter()

from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def admin_login(request: LoginRequest, db: Session = Depends(get_db)):
    # 查找管理员
    admin = db.query(Admin).filter(Admin.username == request.username).first()
    if not admin or not verify_password(request.password, admin.password):  # 使用bcrypt验证密码
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 生成token
    token = create_admin_token(admin.id)
    return {"code": 200, "msg": "success", "data": {"token": token, "admin_id": admin.id}}

@router.post("/logout")
async def admin_logout(current_admin: Admin = Depends(verify_admin_token)):
    # 删除Redis中的Token
    redis = get_redis()
    if redis:
        redis.delete(f"admin:token:{current_admin.id}")
    return {"code": 200, "msg": "退出成功", "data": None}

@router.get("/info")
async def get_admin_info(current_admin: Admin = Depends(verify_admin_token)):
    return {"code": 200, "msg": "success", "data": {"username": current_admin.username, "nickname": current_admin.nickname, "role": current_admin.role}}

@router.put("/notify/setting")
async def set_notify_setting(request: dict, current_admin: Admin = Depends(verify_admin_token)):
    # 保存提醒开关状态到Redis
    redis = get_redis()
    if redis:
        redis.set(f"admin:notify:{current_admin.id}", str(request.get("is_enable")))
    return {"code": 200, "msg": "设置成功", "data": None}

@router.get("/dashboard")
async def get_dashboard_data(current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    # 计算今日订单数和销售额（只统计已支付的订单）
    today = datetime.now().date()
    today_orders = db.query(Order).filter(Order.create_time >= today, Order.pay_status == 1).all()
    today_order_count = len(today_orders)
    today_sales = sum(float(order.total_amount) for order in today_orders)
    
    # 计算本月订单数和销售额（只统计已支付的订单）
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_orders = db.query(Order).filter(Order.create_time >= month_start, Order.pay_status == 1).all()
    month_order_count = len(month_orders)
    month_sales = sum(float(order.total_amount) for order in month_orders)
    
    # 计算待支付订单数
    pending_pay_count = db.query(Order).filter(Order.order_status == 1).count()
    
    # 计算新订单数（只统计已支付的订单）
    new_order_count = len(today_orders)
    
    # 计算超时取消订单数
    timeout_cancel_count = db.query(Order).filter(Order.order_status == 4).count()
    
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "month_order_count": month_order_count,
            "month_sales": month_sales,
            "today_order_count": today_order_count,
            "today_sales": today_sales,
            "pending_pay_count": pending_pay_count,
            "new_order_count": new_order_count,
            "timeout_cancel_count": timeout_cancel_count
        }
    }

@router.get("/product/list")
async def get_admin_product_list(keyword: str = None, status: str = None, page: int = 1, size: int = 10, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    query = db.query(Product).options(joinedload(Product.category))
    
    if keyword:
        query = query.filter(Product.name.like(f"%{keyword}%"))
    
    if status and status != "":
        try:
            status_int = int(status)
            query = query.filter(Product.status == status_int)
        except ValueError:
            pass
    
    total = query.count()
    products = query.offset((page - 1) * size).limit(size).all()
    
    product_list = []
    for product in products:
        product_list.append({
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "status": product.status,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else "未分类",
            "create_time": product.create_time
        })
    
    return {"code": 200, "msg": "success", "data": {"list": product_list, "total": total}}

@router.post("/product/add")
async def add_product(request: dict, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    # 检查分类是否存在
    category_id = request.get("category_id")
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 创建商品
    product = Product(
        name=request.get("name"),
        category_id=category_id,
        price=request.get("price"),
        desc=request.get("desc"),
        cover_img=request.get("cover_img"),
        imgs=json.dumps(request.get("imgs")) if request.get("imgs") else None,
        status=1
    )
    db.add(product)
    db.commit()
    
    # 将商品ID添加到布隆过滤器
    product_bloom_filter.add(str(product.id))
    
    return {"code": 200, "msg": "新增成功", "data": {"product_id": product.id}}

@router.put("/product/{id}")
async def edit_product(id: int, request: dict, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    # 查找商品
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 更新商品信息
    if request.get("name"):
        product.name = request.get("name")
    if request.get("category_id"):
        # 检查分类是否存在
        category = db.query(Category).filter(Category.id == request.get("category_id")).first()
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
        product.category_id = request.get("category_id")
    if request.get("price"):
        product.price = request.get("price")
    if request.get("desc"):
        product.desc = request.get("desc")
    if request.get("cover_img"):
        product.cover_img = request.get("cover_img")
    if request.get("imgs"):
        product.imgs = json.dumps(request.get("imgs"))
    
    db.commit()
    
    # 清空Redis商品缓存
    redis = get_redis()
    if redis:
        redis.delete(f"product:detail:{id}")
    
    return {"code": 200, "msg": "编辑成功", "data": None}

@router.put("/product/{id}/status")
async def update_product_status(id: int, request: dict, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    # 查找商品
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 更新商品状态
    product.status = request.get("status")
    db.commit()
    
    # 清空Redis商品缓存
    redis = get_redis()
    if redis:
        redis.delete(f"product:detail:{id}")
        
        # 主动清理包含该商品的购物车缓存
        carts = db.query(Cart).all()
        for cart in carts:
            items = json.loads(cart.items)
            if any(item['product_id'] == id for item in items):
                redis.delete(f"cart:{cart.user_id}")
    
    return {"code": 200, "msg": "状态更新成功", "data": None}

@router.delete("/product/{id}")
async def delete_product(id: int, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    # 查找商品
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 删除商品
    db.delete(product)
    db.commit()
    
    # 清空Redis商品缓存
    redis = get_redis()
    if redis:
        redis.delete(f"product:detail:{id}")
        
        # 主动清理包含该商品的购物车缓存
        carts = db.query(Cart).all()
        for cart in carts:
            items = json.loads(cart.items)
            if any(item['product_id'] == id for item in items):
                redis.delete(f"cart:{cart.user_id}")
    
    return {"code": 200, "msg": "删除成功", "data": None}

@router.get("/category/list")
async def get_admin_category_list(current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.sort).all()
    
    category_list = []
    for category in categories:
        category_list.append({
            "id": category.id,
            "name": category.name
        })
    
    return {"code": 200, "msg": "success", "data": category_list}

@router.post("/category/add")
async def add_category(request: dict, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    # 创建分类
    category = Category(name=request.get("name"))
    db.add(category)
    db.commit()
    return {"code": 200, "msg": "新增成功", "data": {"category_id": category.id}}

@router.put("/category/{id}")
async def edit_category(id: int, request: dict, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    # 查找分类
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 更新分类名称
    category.name = request.get("name")
    db.commit()
    return {"code": 200, "msg": "编辑成功", "data": None}

@router.delete("/category/{id}")
async def delete_category(id: int, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    # 检查分类是否关联商品
    products = db.query(Product).filter(Product.category_id == id).count()
    if products > 0:
        raise HTTPException(status_code=400, detail="该分类下存在商品，无法删除")
    
    # 查找分类
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 删除分类
    db.delete(category)
    db.commit()
    return {"code": 200, "msg": "删除成功", "data": None}

@router.get("/user/list")
async def get_admin_user_list(phone: str = None, nickname: str = None, page: int = 1, size: int = 10, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    query = db.query(User)
    
    if phone:
        query = query.filter(User.phone.like(f"%{phone}%"))
    
    if nickname:
        query = query.filter(User.nickname.like(f"%{nickname}%"))
    
    total = query.count()
    users = query.offset((page - 1) * size).limit(size).all()
    
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "nickname": user.nickname,
            "phone": user.phone
        })
    
    return {"code": 200, "msg": "success", "data": {"list": user_list, "total": total}}

@router.get("/user/{id}")
async def get_user_detail(id: int, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"code": 200, "msg": "success", "data": {
        "id": user.id,
        "nickname": user.nickname,
        "phone": user.phone,
        "address": user.address
    }}

@router.get("/order/list")
async def get_admin_order_list(order_no: str = None, user_id: int = None, pay_status: int = None, order_status: int = None, create_time: str = None, page: int = 1, size: int = 10, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    query = db.query(Order)
    
    if order_no:
        query = query.filter(Order.order_no.like(f"%{order_no}%"))
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    if pay_status is not None:
        query = query.filter(Order.pay_status == pay_status)
    
    if order_status is not None:
        query = query.filter(Order.order_status == order_status)
    
    if create_time:
        try:
            date = datetime.strptime(create_time, "%Y-%m-%d")
            query = query.filter(Order.create_time >= date)
        except:
            pass
    
    total = query.count()
    orders = query.order_by(Order.create_time.desc()).offset((page - 1) * size).limit(size).all()
    
    order_list = []
    for order in orders:
        # 获取订单项
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        items = []
        for item in order_items:
            # 查询商品信息，获取商品名称
            product = db.query(Product).filter(Product.id == item.product_id).first()
            product_name = product.name if product else f"商品ID: {item.product_id}"
            items.append({
                "product_id": item.product_id,
                "product_name": product_name,
                "quantity": item.quantity,
                "price": float(item.price)
            })
        
        order_list.append({
            "order_id": order.id,
            "order_no": order.order_no,
            "user_id": order.user_id,
            "total_amount": float(order.total_amount),
            "pay_status": order.pay_status,
            "order_status": order.order_status,
            "create_time": order.create_time.isoformat(),
            "items": items
        })
    
    return {"code": 200, "msg": "success", "data": {"list": order_list, "total": total}}

@router.get("/order/{id}")
async def get_order_detail(id: int, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 获取订单项
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    items = []
    for item in order_items:
        # 查询商品信息，获取商品名称
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product_name = product.name if product else f"商品ID: {item.product_id}"
        items.append({
            "product_id": item.product_id,
            "product_name": product_name,
            "quantity": item.quantity,
            "price": float(item.price)
        })
    
    return {"code": 200, "msg": "success", "data": {
        "order_id": order.id,
        "order_no": order.order_no,
        "total_amount": float(order.total_amount),
        "pay_status": order.pay_status,
        "order_status": order.order_status,
        "address": order.address,
        "phone": order.phone,
        "consignee": order.consignee,
        "create_time": order.create_time.isoformat(),
        "pay_time": order.pay_time.isoformat() if order.pay_time else None,
        "items": items
    }}

@router.put("/order/{id}/cancel")
async def cancel_order(id: int, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    # 查找订单
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.order_status != 1:
        return {"code": 400, "msg": "订单状态错误，只能取消待支付的订单", "data": None}
    
    # 取消订单
    order.order_status = 4  # 已取消
    # 支付状态保持为0（未支付），因为订单被取消，实际未支付
    db.commit()
    
    # 清除Redis缓存
    redis = get_redis()
    if redis:
        # 清除订单状态缓存
        redis.delete(f"order:status:{order.id}")
        # 清除订单超时缓存
        redis.delete(f"order:timeout:{order.id}")
        # 清除所有可能的订单列表缓存
        pattern = f"order:list:*"
        keys = redis.keys(pattern)
        if keys:
            redis.delete(*keys)
    
    # 广播订单状态更新消息
    from app.core.websocket import broadcast_message
    broadcast_message({
        "type": "order_status",
        "data": {
            "order_id": order.id,
            "order_status": order.order_status
        }
    })
    
    return {"code": 200, "msg": "取消成功", "data": None}

@router.get("/pay/list")
async def get_pay_list(order_no: str = None, transaction_id: str = None, pay_status: int = None, page: int = 1, size: int = 10, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    query = db.query(Order).filter(Order.pay_status != 0)
    
    if order_no:
        query = query.filter(Order.order_no.like(f"%{order_no}%"))
    
    if transaction_id:
        query = query.filter(Order.transaction_id.like(f"%{transaction_id}%"))
    
    if pay_status is not None:
        query = query.filter(Order.pay_status == pay_status)
    
    total = query.count()
    orders = query.order_by(Order.create_time.desc()).offset((page - 1) * size).limit(size).all()
    
    pay_list = []
    for order in orders:
        pay_list.append({
            "id": order.id,
            "order_no": order.order_no,
            "transaction_id": order.transaction_id,
            "pay_status": order.pay_status,
            "pay_time": order.pay_time.isoformat() if order.pay_time else None
        })
    
    return {"code": 200, "msg": "success", "data": {"list": pay_list, "total": total}}

@router.get("/pay/{id}")
async def get_pay_detail(id: int, current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    
    return {"code": 200, "msg": "success", "data": {
        "id": order.id,
        "order_no": order.order_no,
        "transaction_id": order.transaction_id,
        "pay_status": order.pay_status,
        "pay_time": order.pay_time.isoformat() if order.pay_time else None
    }}

@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...), current_admin: Admin = Depends(verify_admin_token)):
    """上传图片
    
    Args:
        file: 上传的图片文件
        current_admin: 当前管理员
        
    Returns:
        dict: 上传成功后的图片路径
    """
    # 确保uploads目录存在
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, file_name)
    
    # 保存文件
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    
    # 返回图片路径
    image_url = f"/uploads/{file_name}"
    return {"code": 200, "msg": "上传成功", "data": {"url": image_url}}
