from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.auth import verify_admin_token
from app.core.redis import get_redis
from app.models import Order, OrderItem, Product, User, Admin
from typing import Dict, Any, List

router = APIRouter()

@router.get("/sales")
async def get_sales_statistics(period: str = "day", current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    """获取销售统计数据
    period: day, week, month, year
    """
    try:
        # 尝试从缓存获取
        redis = get_redis()
        if redis:
            cache_key = f"statistics:sales:{period}"
            cached_data = redis.get(cache_key)
            if cached_data:
                import json
                return json.loads(cached_data)
        
        # 计算时间范围
        now = datetime.now()
        if period == "day":
            start_time = now - timedelta(days=1)
            time_format = "%H:00"
        elif period == "week":
            start_time = now - timedelta(days=7)
            time_format = "%m-%d"
        elif period == "month":
            start_time = now - timedelta(days=30)
            time_format = "%m-%d"
        elif period == "year":
            start_time = now - timedelta(days=365)
            time_format = "%Y-%m"
        else:
            start_time = now - timedelta(days=1)
            time_format = "%H:00"
        
        # 查询销售额和订单数
        sales_data = db.query(
            func.date_format(Order.create_time, time_format).label("time"),
            func.sum(Order.total_amount).label("sales"),
            func.count(Order.id).label("orders")
        ).filter(
            Order.create_time >= start_time,
            Order.order_status >= 2  # 已支付订单
        ).group_by("time").all()
        
        # 格式化数据
        labels = []
        sales_values = []
        orders_values = []
        
        for item in sales_data:
            labels.append(item.time)
            sales_values.append(float(item.sales) if item.sales else 0)
            orders_values.append(item.orders)
        
        # 计算汇总数据
        total_sales = sum(sales_values)
        total_orders = sum(orders_values)
        average_order = total_sales / total_orders if total_orders > 0 else 0
        
        result = {
            "code": 200,
            "msg": "success",
            "data": {
                "labels": labels,
                "sales": sales_values,
                "orders": orders_values,
                "summary": {
                    "total_sales": total_sales,
                    "total_orders": total_orders,
                    "average_order": round(average_order, 2)
                }
            }
        }
        
        # 缓存结果
        if redis:
            import json
            redis.set(cache_key, json.dumps(result), ex=3600)
        
        return result
    except Exception as e:
        return {"code": 500, "msg": "获取销售统计失败", "error": str(e)}

@router.get("/products")
async def get_product_statistics(current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    """获取商品统计数据"""
    try:
        # 尝试从缓存获取
        redis = get_redis()
        if redis:
            cache_key = "statistics:products"
            cached_data = redis.get(cache_key)
            if cached_data:
                import json
                return json.loads(cached_data)
        
        # 热销商品
        hot_products = db.query(
            Product.id,
            Product.name,
            Product.price,
            func.sum(OrderItem.quantity).label("sales_count"),
            func.sum(OrderItem.quantity * OrderItem.price).label("sales_amount")
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.order_status >= 2  # 已支付订单
        ).group_by(
            Product.id
        ).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(10).all()
        

        
        # 格式化数据
        hot_products_list = []
        for product in hot_products:
            hot_products_list.append({
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "sales_count": product.sales_count,
                "sales_amount": float(product.sales_amount)
            })
        

        
        result = {
            "code": 200,
            "msg": "success",
            "data": {
                "hot_products": hot_products_list
            }
        }
        
        # 缓存结果
        if redis:
            import json
            redis.set(cache_key, json.dumps(result), ex=3600)
        
        return result
    except Exception as e:
        return {"code": 500, "msg": "获取商品统计失败", "error": str(e)}

@router.get("/users")
async def get_user_statistics(period: str = "day", current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    """获取用户统计数据
    period: day, week, month, year
    """
    try:
        # 尝试从缓存获取
        redis = get_redis()
        if redis:
            cache_key = f"statistics:users:{period}"
            cached_data = redis.get(cache_key)
            if cached_data:
                import json
                return json.loads(cached_data)
        
        # 计算时间范围
        now = datetime.now()
        if period == "day":
            start_time = now - timedelta(days=1)
            time_format = "%H:00"
        elif period == "week":
            start_time = now - timedelta(days=7)
            time_format = "%m-%d"
        elif period == "month":
            start_time = now - timedelta(days=30)
            time_format = "%m-%d"
        elif period == "year":
            start_time = now - timedelta(days=365)
            time_format = "%Y-%m"
        else:
            start_time = now - timedelta(days=1)
            time_format = "%H:00"
        
        # 查询用户注册数据
        user_data = db.query(
            func.date_format(User.create_time, time_format).label("time"),
            func.count(User.id).label("count")
        ).filter(
            User.create_time >= start_time
        ).group_by("time").all()
        
        # 格式化数据
        labels = []
        values = []
        
        for item in user_data:
            labels.append(item.time)
            values.append(item.count)
        
        # 计算总用户数
        total_users = db.query(func.count(User.id)).scalar()
        
        result = {
            "code": 200,
            "msg": "success",
            "data": {
                "labels": labels,
                "values": values,
                "total_users": total_users
            }
        }
        
        # 缓存结果
        if redis:
            import json
            redis.set(cache_key, json.dumps(result), ex=3600)
        
        return result
    except Exception as e:
        return {"code": 500, "msg": "获取用户统计失败", "error": str(e)}

@router.get("/orders")
async def get_order_statistics(current_admin: Admin = Depends(verify_admin_token), db: Session = Depends(get_db)):
    """获取订单统计数据"""
    try:
        # 尝试从缓存获取
        redis = get_redis()
        if redis:
            cache_key = "statistics:orders"
            cached_data = redis.get(cache_key)
            if cached_data:
                import json
                return json.loads(cached_data)
        
        # 订单状态分布
        order_status_data = db.query(
            Order.order_status,
            func.count(Order.id).label("count")
        ).group_by(Order.order_status).all()
        
        # 订单状态映射
        status_map = {
            0: "待付款",
            1: "待发货",
            2: "待收货",
            3: "已完成",
            4: "已取消"
        }
        
        # 格式化数据
        status_distribution = []
        for item in order_status_data:
            status_distribution.append({
                "status": item.order_status,
                "status_name": status_map.get(item.order_status, "未知"),
                "count": item.count
            })
        
        # 计算平均支付时间
        payment_time_data = db.query(
            func.avg(func.timestampdiff(func.SECOND, Order.create_time, Order.pay_time)).label("avg_payment_time")
        ).filter(
            Order.pay_time.isnot(None)
        ).scalar()
        
        avg_payment_time = round(payment_time_data / 60, 2) if payment_time_data else 0
        
        result = {
            "code": 200,
            "msg": "success",
            "data": {
                "status_distribution": status_distribution,
                "avg_payment_time": avg_payment_time  # 单位：分钟
            }
        }
        
        # 缓存结果
        if redis:
            import json
            redis.set(cache_key, json.dumps(result), ex=3600)
        
        return result
    except Exception as e:
        return {"code": 500, "msg": "获取订单统计失败", "error": str(e)}
