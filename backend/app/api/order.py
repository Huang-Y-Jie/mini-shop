from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import json
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import verify_user_token
from app.core.redis import get_redis
from app.core.config import settings
from app.core.websocket import broadcast_message
from app.core.logger import log_action
from app.models import Order, OrderItem, Cart, Product, User, RegionShipping

router = APIRouter()

class OrderCreate(BaseModel):
    address: str = ""
    phone: str = ""
    consignee: str = ""
    region_id: int  # 地区ID
    product_ids: str = ""  # 直接购买时的商品ID，逗号分隔
    quantity: int = 1  # 直接购买时的商品数量

@router.post("/create")
async def create_order(request: Request, order_data: OrderCreate, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    try:
        # 获取幂等性ID
        req_id = request.headers.get("X-Request-Id")
        if not req_id:
            log_action("order", str(current_user.id), "create", "fail", "缺少X-Request-Id头")
            raise HTTPException(status_code=400, detail="缺少X-Request-Id头")
        
        # 检查幂等性
        redis = get_redis()
        if redis and req_id:
            if redis.exists(f"order:req:{req_id}"):
                log_action("order", str(current_user.id), "create", "fail", "重复下单，请求已处理")
                return {"code": 409, "msg": "重复下单，请求已处理", "data": None}
            
            # 标记请求已处理
            redis.set(f"order:req:{req_id}", "1", ex=5*60)  # 5分钟过期
        
        # 检查是否是直接购买
        if order_data.product_ids:
            # 直接购买的情况
            product_ids_list = order_data.product_ids.split(',')
            product_id = product_ids_list[0]  # 直接购买只支持单个商品
            quantity = order_data.quantity
            
            # 检查商品是否存在且上架
            product = db.query(Product).filter(Product.id == product_id, Product.status == 1).first()
            if not product:
                log_action("order", str(current_user.id), "create", "fail", f"商品{product_id}已下架，无法购买")
                return {"code": 410, "msg": f"商品{product_id}已下架，无法购买", "data": None}
            
            # 计算总金额
            total_amount = product.price * quantity
            order_items = [{
                "product_id": product_id,
                "price": product.price,
                "quantity": quantity
            }]
            product_ids = [product_id]
        else:
            # 从购物车结算的情况
            cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
            if not cart:
                log_action("order", str(current_user.id), "create", "fail", "购物车为空")
                return {"code": 400, "msg": "购物车为空", "data": None}
            
            # 解析购物车商品项
            cart_items = json.loads(cart.items)
            
            # 使用购物车中的所有商品
            selected_items = cart_items
            if not selected_items:
                log_action("order", str(current_user.id), "create", "fail", "购物车为空")
                return {"code": 400, "msg": "购物车为空", "data": None}
            
            # 计算总金额并检查商品状态
            total_amount = 0
            order_items = []
            product_ids = []
            for item in selected_items:
                product = db.query(Product).filter(Product.id == item['product_id'], Product.status == 1).first()
                if not product:
                    log_action("order", str(current_user.id), "create", "fail", f"商品{item['product_id']}已下架，无法购买")
                    return {"code": 410, "msg": f"商品{item['product_id']}已下架，无法购买", "data": None}
                
                total_amount += product.price * item['quantity']
                order_items.append({
                    "product_id": item['product_id'],
                    "price": product.price,
                    "quantity": item['quantity']
                })
                product_ids.append(item['product_id'])
            
            # 从购物车中移除已结算的商品
            remaining_items = [item for item in cart_items if item['product_id'] not in product_ids]
            cart.items = json.dumps(remaining_items)
        
        # 查询地区运费
        region = db.query(RegionShipping).filter(RegionShipping.id == order_data.region_id, RegionShipping.is_active == 1).first()
        if not region:
            log_action("order", str(current_user.id), "create", "fail", f"地区ID {order_data.region_id} 不存在或未启用")
            return {"code": 400, "msg": "所选地区不存在或未启用", "data": None}
        
        # 计算运费
        shipping_fee = region.shipping_fee
        
        # 计算总金额（商品金额 + 运费）
        from decimal import Decimal
        total_amount_with_shipping = total_amount + Decimal(str(shipping_fee))
        
        # 生成订单号
        order_no = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
        
        # 计算过期时间
        expire_time = datetime.now() + timedelta(minutes=settings.ORDER_TIMEOUT_MINUTES)
        
        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=current_user.id,
            total_amount=total_amount_with_shipping,
            pay_status=0,
            order_status=1,
            address=order_data.address or "",
            phone=order_data.phone or "",
            consignee=order_data.consignee or "",
            region_id=order_data.region_id,
            expire_time=expire_time
        )
        db.add(order)
        db.flush()  # 获取订单ID
        
        # 创建订单项
        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                price=item["price"],
                quantity=item["quantity"]
            )
            db.add(order_item)
        
        # 减少商品库存
        # 由于开发文档中未定义stock和sales字段，此处注释掉相关逻辑
        # for item in order_items:
        #     product = db.query(Product).filter(Product.id == item["product_id"]).first()
        #     if product and hasattr(product, 'stock'):
        #         product.stock -= item["quantity"]
        #         if hasattr(product, 'sales'):
        #             product.sales += item["quantity"]
        
        db.commit()
        
        # 缓存订单状态
        if redis:
            redis.set(f"order:status:{order.id}", "待支付", ex=24*60*60)  # 24小时过期
            
            # 设置订单超时Key
            redis.set(f"order:timeout:{order.id}", order.id, ex=settings.ORDER_TIMEOUT_MINUTES*60)
        
        # 广播新订单消息
        broadcast_message({
            "type": "new_order",
            "data": {
                "order_id": order.id,
                "order_no": order_no,
                "total_amount": float(total_amount),
                "create_time": order.create_time.isoformat()
            }
        })
        
        log_action("order", str(current_user.id), "create", "success", f"订单号: {order_no}")
        return {"code": 200, "msg": "success", "data": {"order_id": order.id, "order_no": order_no, "total_amount": float(total_amount_with_shipping)}}
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"订单创建错误: {error_traceback}")
        log_action("order", str(current_user.id), "create", "fail", f"{str(e)}\n{error_traceback}")
        # 返回具体的错误信息，而不是直接抛出异常
        return {"code": 500, "msg": f"创建订单失败: {str(e)}", "data": None}

@router.get("/list")
async def get_order_list(pay_status: int = None, order_status: int = None, page: int = 1, size: int = 10, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """获取订单列表
    
    Args:
        pay_status: 支付状态，可选
        order_status: 订单状态，可选
        page: 页码，默认1
        size: 每页数量，默认10
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 订单列表和总数
    """
    # 构建缓存键
    cache_key = f"order:list:{current_user.id}:{pay_status or 'all'}:{order_status or 'all'}:{page}:{size}"
    
    # 尝试从Redis获取
    redis = get_redis()
    if redis:
        cached_data = redis.get(cache_key)
        if cached_data:
            import json
            return {"code": 200, "msg": "success", "data": json.loads(cached_data)}
    
    # 从数据库获取，使用关联查询避免N+1问题
    from sqlalchemy.orm import joinedload
    
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    if pay_status is not None:
        query = query.filter(Order.pay_status == pay_status)
    
    if order_status is not None:
        query = query.filter(Order.order_status == order_status)
    
    total = query.count()
    # 使用joinedload预加载订单项，避免N+1查询
    orders = query.options(joinedload(Order.items)).order_by(Order.create_time.desc()).offset((page - 1) * size).limit(size).all()
    
    order_list = []
    for order in orders:
        items = []
        for item in order.items:
            # 查询商品信息，获取商品名称和图片
            product = db.query(Product).filter(Product.id == item.product_id).first()
            product_name = product.name if product else f"商品ID: {item.product_id}"
            product_image = product.cover_img if product and product.cover_img else ""
            items.append({
                "product_id": item.product_id,
                "product_name": product_name,
                "quantity": item.quantity,
                "price": item.price,
                "cover_img": product_image
            })
        
        order_list.append({
            "order_id": order.id,
            "order_no": order.order_no,
            "total_amount": float(order.total_amount),
            "pay_status": order.pay_status,
            "order_status": order.order_status,
            "create_time": order.create_time.isoformat(),
            "items": items
        })
    
    result = {"list": order_list, "total": total}
    
    # 缓存结果
    if redis:
        import json
        redis.set(cache_key, json.dumps(result), ex=5*60)  # 5分钟过期
    
    return {"code": 200, "msg": "success", "data": result}

@router.get("/{id}")
async def get_order_detail(id: int, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """获取订单详情
    
    Args:
        id: 订单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 订单详细信息
        
    Raises:
        HTTPException: 订单不存在时抛出404异常
    """
    # 构建缓存键
    cache_key = f"order:detail:{current_user.id}:{id}"
    
    # 尝试从Redis获取
    redis = get_redis()
    if redis:
        cached_data = redis.get(cache_key)
        if cached_data:
            import json
            return {"code": 200, "msg": "success", "data": json.loads(cached_data)}
    
    # 从数据库获取，使用关联查询避免N+1问题
    from sqlalchemy.orm import joinedload
    
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 构建订单项
    items = []
    for item in order.items:
        # 查询商品信息，获取商品名称和图片
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product_name = product.name if product else f"商品ID: {item.product_id}"
        product_image = product.cover_img if product and product.cover_img else ""
        items.append({
            "product_id": item.product_id,
            "product_name": product_name,
            "quantity": item.quantity,
            "price": item.price,
            "cover_img": product_image
        })
    
    # 尝试从address表获取地址信息
    from app.models import Address
    address = db.query(Address).filter(Address.user_id == current_user.id, Address.is_default == 1).first()
    address_str = order.address
    
    # 检查address_str是否为空或默认值
    if not address_str or address_str == "value" or address_str == "":
        if address:
            address_str = f"{address.province}{address.city}{address.district}{address.detail}"
        else:
            # 如果没有默认地址，尝试获取第一个地址
            address = db.query(Address).filter(Address.user_id == current_user.id).first()
            if address:
                address_str = f"{address.province}{address.city}{address.district}{address.detail}"
            else:
                address_str = ""  
    
    # 确保phone和consignee有值
    phone = order.phone
    consignee = order.consignee
    if not phone and address:
        phone = address.phone
    if not consignee and address:
        consignee = address.name
    
    order_detail = {
        "order_id": order.id,
        "order_no": order.order_no,
        "total_amount": float(order.total_amount),
        "pay_status": order.pay_status,
        "order_status": order.order_status,
        "address": address_str,
        "phone": phone or "",
        "consignee": consignee or "",
        "create_time": order.create_time.isoformat(),
        "pay_time": order.pay_time.isoformat() if order.pay_time else None,
        "items": items
    }
    
    # 缓存结果
    if redis:
        import json
        redis.set(cache_key, json.dumps(order_detail), ex=10*60)  # 10分钟过期
    
    return {
        "code": 200,
        "msg": "success",
        "data": order_detail
    }

@router.put("/{id}/cancel")
async def cancel_order(id: int, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.order_status != 1:
        return {"code": 400, "msg": "订单状态错误，只能取消待支付的订单", "data": None}
    
    # 取消订单
    order.order_status = 4  # 已取消
    # 支付状态保持为0（未支付），因为订单被取消，实际未支付
    
    # 恢复商品库存
    # 由于开发文档中未定义stock和sales字段，此处注释掉相关逻辑
    
    db.commit()
    
    # 清除Redis缓存
    redis = get_redis()
    if redis:
        # 清除订单状态缓存
        redis.delete(f"order:status:{order.id}")
        # 清除订单超时缓存
        redis.delete(f"order:timeout:{order.id}")
        # 清除订单详情缓存
        redis.delete(f"order:detail:{current_user.id}:{order.id}")
        # 清除所有可能的订单列表缓存
        pattern = f"order:list:{current_user.id}:*"
        keys = redis.keys(pattern)
        if keys:
            redis.delete(*keys)
    
    # 广播订单状态更新消息
    broadcast_message({
        "type": "order_status",
        "data": {
            "order_id": order.id,
            "order_status": order.order_status
        }
    })
    
    return {"code": 200, "msg": "取消成功", "data": None}

@router.put("/{id}/receive")
async def receive_order(id: int, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    """确认收货
    
    Args:
        id: 订单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        dict: 操作结果
        
    Raises:
        HTTPException: 订单不存在时抛出404异常
        HTTPException: 订单状态错误时抛出400异常
    """
    # 查找订单
    order = db.query(Order).filter(Order.id == id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 检查订单状态
    if order.order_status != 2:
        raise HTTPException(status_code=400, detail="订单状态错误，只能确认已支付的订单")
    
    # 更新订单状态
    order.order_status = 3  # 已完成
    db.commit()
    
    # 更新Redis缓存
    redis = get_redis()
    if redis:
        redis.set(f"order:status:{order.id}", "已完成", ex=24*60*60)
        # 清除订单列表和详情缓存
        redis.delete(f"order:detail:{current_user.id}:{order.id}")
        # 清除所有可能的订单列表缓存
        import glob
        pattern = f"order:list:{current_user.id}:*"
        keys = redis.keys(pattern)
        if keys:
            redis.delete(*keys)
    
    # 广播订单状态更新消息
    broadcast_message({
        "type": "order_status",
        "data": {
            "order_id": order.id,
            "order_status": order.order_status
        }
    })
    
    return {"code": 200, "msg": "确认收货成功", "data": None}
