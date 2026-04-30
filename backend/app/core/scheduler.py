import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.config import settings
from app.models import Order

logger = logging.getLogger(__name__)

async def check_order_timeout():
    """检查订单超时并处理"""
    logger.info("开始检查订单超时")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 获取当前时间
        now = datetime.now()
        
        # 查询所有超时未支付的订单
        timeout_orders = db.query(Order).filter(
            Order.order_status == 1,  # 待支付状态
            Order.pay_status == 0,  # 未支付
            Order.expire_time < now  # 已过期
        ).all()
        
        if not timeout_orders:
            logger.info("没有超时订单")
            return
        
        # 处理每个超时订单
        for order in timeout_orders:
            logger.info(f"处理超时订单: {order.order_no}")
            
            # 更新订单状态为超时取消
            order.order_status = 5  # 超时取消
            order.pay_status = 0  # 未支付
            
            # 清除Redis中的订单状态和超时键
            redis = get_redis()
            if redis:
                redis.delete(f"order:status:{order.id}")
                redis.delete(f"order:timeout:{order.id}")
                # 清除订单列表和详情缓存
                pattern = f"order:list:{order.user_id}:*"
                keys = redis.keys(pattern)
                if keys:
                    redis.delete(*keys)
                redis.delete(f"order:detail:{order.user_id}:{order.id}")
        
        # 提交事务
        db.commit()
        logger.info(f"处理了 {len(timeout_orders)} 个超时订单")
        
    except Exception as e:
        logger.error(f"检查订单超时出错: {str(e)}")
        db.rollback()
    finally:
        db.close()

async def run_scheduler():
    """运行定时任务调度器"""
    logger.info("启动定时任务调度器")
    
    while True:
        try:
            # 每1分钟检查一次订单超时
            await check_order_timeout()
            await asyncio.sleep(60)  # 休眠1分钟
        except Exception as e:
            logger.error(f"定时任务出错: {str(e)}")
            await asyncio.sleep(60)  # 出错后继续执行
