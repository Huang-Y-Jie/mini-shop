from fastapi import Request, HTTPException
from app.core.redis import get_redis
import time
import redis

class RateLimitMiddleware:
    """请求频率限制中间件
    
    根据不同的接口路径设置不同的限流策略
    """
    
    # 限流配置
    RATE_LIMIT_CONFIG = {
        # 订单相关
        "/api/order/create": {
            "limit": 5,  # 每分钟最多5次请求
            "window": 60  # 60秒窗口
        },
        "/api/pay/wxpay": {
            "limit": 5,
            "window": 60
        },
        # 用户相关
        "/api/user/auth": {
            "limit": 10,
            "window": 60
        },
        # 购物车相关
        "/api/cart/items": {
            "limit": 20,
            "window": 60
        },
        # 商品相关
        "/api/product/list": {
            "limit": 30,
            "window": 60
        },
        "/api/product/category/list": {
            "limit": 10,
            "window": 60
        },
        # 地址相关
        "/api/address/": {
            "limit": 10,
            "window": 60
        },
        # 统计相关
        "/api/statistics/": {
            "limit": 5,
            "window": 60
        }
    }
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            # 创建请求对象
            request = Request(scope, receive)
            # 获取客户端IP
            client_ip = request.client.host
            
            # 检查是否需要限流
            path = request.url.path
            config = self._get_rate_limit_config(path)
            
            if config:
                # 构建限流key
                rate_limit_key = f"rate_limit:{client_ip}:{path}"
                redis_client = get_redis()
                
                # 检查是否达到限流阈值
                if redis_client:
                    try:
                        current = redis_client.get(rate_limit_key)
                        if current and int(current) >= config["limit"]:
                            # 返回限流响应
                            from fastapi.responses import JSONResponse
                            response = JSONResponse(
                                status_code=429,  # 429 Too Many Requests
                                content={"code": 429, "msg": "操作过于频繁，请稍后重试", "data": None}
                            )
                            await response(scope, receive, send)
                            return
                        
                        # 增加计数
                        if current:
                            redis_client.incr(rate_limit_key)
                        else:
                            redis_client.set(rate_limit_key, 1, ex=config["window"])
                    except redis.RedisError:
                        # Redis操作失败，跳过限流
                        pass
        
        await self.app(scope, receive, send)
    
    def _get_rate_limit_config(self, path):
        """获取路径对应的限流配置
        
        Args:
            path: 请求路径
            
        Returns:
            dict: 限流配置，如果没有配置则返回None
        """
        # 精确匹配
        if path in self.RATE_LIMIT_CONFIG:
            return self.RATE_LIMIT_CONFIG[path]
        
        # 前缀匹配
        for config_path, config in self.RATE_LIMIT_CONFIG.items():
            if config_path.endswith('/') and path.startswith(config_path):
                return config
        
        return None