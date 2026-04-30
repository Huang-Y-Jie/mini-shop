import redis
import threading
import asyncio
import time
from .config import settings

redis_client = None
pubsub = None
redis_available = None
last_check_time = 0

# 处理Redis过期事件
def handle_expired_key(message):
    """处理Redis键过期事件"""
    if message and 'data' in message:
        key = message['data'].decode('utf-8')
        if key.startswith('order:timeout:'):
            # 处理订单超时
            order_id = key.split(':')[-1]
            handle_order_timeout(order_id)

def handle_order_timeout(order_id):
    """处理订单超时"""
    from app.models import Order
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # 查询订单
        order = db.query(Order).filter(Order.id == int(order_id), Order.order_status == 1).first()
        if order:
            # 更新订单状态为超时取消
            order.order_status = 4
            order.pay_status = 0
            db.commit()
            
            # 更新Redis缓存
            redis = get_redis()
            if redis:
                redis.set(f"order:status:{order_id}", "超时取消", ex=24*60*60)
                
            # 广播订单状态更新
            from .websocket import broadcast_message
            broadcast_message({
                "type": "order_timeout",
                "data": {
                    "order_id": int(order_id),
                    "order_status": 4
                }
            })
    except Exception as e:
        print(f"处理订单超时失败: {e}")
    finally:
        db.close()

def start_redis_listener():
    """启动Redis过期事件监听器"""
    global pubsub
    redis = get_redis()
    if redis:
        try:
            # 订阅过期事件
            pubsub = redis.pubsub()
            pubsub.subscribe('__keyevent@0__:expired')
            
            # 开始监听
            for message in pubsub.listen():
                if message['type'] == 'message':
                    handle_expired_key(message)
        except Exception as e:
            print(f"Redis监听器启动失败: {e}")

def get_redis():
    global redis_client, redis_available, last_check_time
    current_time = time.time()
    
    # 5分钟内不再检查Redis可用性
    if current_time - last_check_time < 300:
        if not redis_available:
            return None
    
    if not redis_client:
        try:
            print(f"尝试连接Redis: {settings.REDIS_URL}")
            # 设置连接超时为0.5秒，进一步减少超时时间
            redis_client = redis.from_url(
                settings.REDIS_URL, 
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5
            )
            # 测试连接
            redis_client.ping()
            print("Redis连接成功")
            
            # 检查并开启过期事件通知
            config = redis_client.config_get('notify-keyspace-events')
            if config.get('notify-keyspace-events', '') != 'Ex':
                redis_client.config_set('notify-keyspace-events', 'Ex')
                print("已开启Redis过期事件通知")
            
            # 启动过期事件监听器
            threading.Thread(target=start_redis_listener, daemon=True).start()
            print("Redis监听器启动成功")
            
            # 更新连接状态
            redis_available = True
            last_check_time = current_time
        except redis.RedisError as e:
            # Redis连接失败，返回None
            print(f"Redis连接失败: {str(e)}")
            redis_available = False
            last_check_time = current_time
            return None
    else:
        # 检查连接是否有效
        try:
            redis_client.ping()
            redis_available = True
            last_check_time = current_time
        except redis.RedisError:
            # 连接失效，重置为None
            redis_client = None
            redis_available = False
            last_check_time = current_time
            return None
    return redis_client