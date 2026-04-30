from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import threading
import redis
import asyncio
import os
from app.core.database import engine, Base, SessionLocal, get_db
from sqlalchemy.orm import Session
from app.core.redis import get_redis
from app.core.websocket import broadcast_message
from app.core.rate_limit import RateLimitMiddleware
from app.core.bloom_filter import product_bloom_filter
from app.core.exception import redis_exception_handler, general_exception_handler
from app.core.scheduler import run_scheduler
from app.core.config import settings
from app.models import Order, OrderItem, Product, Banner
from app.api import user, product, cart, order, pay, admin, address, statistics, banner, region
from app.core.websocket import router as websocket_router
from datetime import datetime

# 创建上传目录
os.makedirs(settings.IMAGE_LOCAL_PATH, exist_ok=True)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 初始化布隆过滤器
db = SessionLocal()
try:
    products = db.query(Product).all()
    for prod in products:
        product_bloom_filter.add(str(prod.id))
finally:
    db.close()

app = FastAPI(
    title="商城API",
    description="线上商城小程序后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加限流中间件
# app.add_middleware(RateLimitMiddleware)

# 注册路由
app.include_router(user, prefix="/api/user", tags=["user"])
app.include_router(product, prefix="/api/product", tags=["product"])
app.include_router(cart, prefix="/api/cart", tags=["cart"])
app.include_router(order, prefix="/api/order", tags=["order"])
app.include_router(pay, prefix="/api/pay", tags=["pay"])
app.include_router(admin, prefix="/api/admin", tags=["admin"])
app.include_router(address, prefix="/api/address", tags=["address"])
app.include_router(statistics, prefix="/api/statistics", tags=["statistics"])
app.include_router(banner, prefix="/api/banner", tags=["banner"])
app.include_router(region, prefix="/api/region", tags=["region"])
app.include_router(websocket_router, tags=["websocket"])

# 注册异常处理器
app.add_exception_handler(redis.RedisError, redis_exception_handler)
# app.add_exception_handler(Exception, general_exception_handler)

# 启动定时任务调度器
def start_scheduler():
    asyncio.run(run_scheduler())

# 启动定时任务调度器线程
threading.Thread(target=start_scheduler, daemon=True).start()

# 启动WebSocket连接清理任务
import asyncio
from app.core.websocket import start_connection_cleanup
threading.Thread(target=lambda: asyncio.run(start_connection_cleanup()), daemon=True).start()

# 购物车数据定时同步
import json
from app.models import Cart

def sync_cart_data():
    import time
    while True:
        try:
            db = SessionLocal()
            redis = get_redis()
            
            # 只有当Redis可用时才同步数据
            if redis:
                # 获取所有购物车
                carts = db.query(Cart).all()
                for cart in carts:
                    # 从Redis获取最新数据
                    cart_data = redis.get(f"cart:{cart.user_id}")
                    if cart_data:
                        # 更新数据库
                        cart.items = cart_data
                        db.commit()
                
                print("购物车数据同步完成")
            else:
                print("Redis不可用，跳过购物车数据同步")
        except Exception as e:
            print(f"购物车数据同步失败: {e}")
        finally:
            db.close()
        
        # 每5分钟同步一次
        time.sleep(300)

# 启动定时任务
threading.Thread(target=sync_cart_data, daemon=True).start()

# 挂载静态文件服务
app.mount("/uploads", StaticFiles(directory=settings.IMAGE_LOCAL_PATH), name="uploads")

@app.get("/")
def read_root():
    return {"message": "商城API服务运行中"}

@app.get("/test")
def test():
    return {"code": 200, "msg": "success", "data": {"message": "测试成功"}}

@app.get("/test/admin")
def test_admin(db: Session = Depends(get_db)):
    from app.models import Admin
    admin = db.query(Admin).first()
    if admin:
        return {"code": 200, "msg": "success", "data": {"id": admin.id, "username": admin.username, "password": admin.password}}
    else:
        return {"code": 404, "msg": "admin用户不存在", "data": None}

# 添加一个简单的测试接口，用于检查数据库连接
@app.get("/test/db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # 尝试执行一个简单的查询
        from app.models import Product
        count = db.query(Product).count()
        return {"code": 200, "msg": "success", "data": {"count": count}}
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        import traceback
        print(traceback.format_exc())
        return {"code": 500, "msg": "数据库连接失败", "data": None}

# 图片上传接口
@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """上传图片"""
    try:
        # 生成文件名
        import uuid
        file_ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(settings.IMAGE_LOCAL_PATH, filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 返回图片URL
        image_url = f"{settings.IMAGE_BASE_URL}/{filename}"
        return {"code": 200, "msg": "success", "data": {"url": image_url}}
    except Exception as e:
        return {"code": 500, "msg": f"上传失败: {str(e)}"}

# main.py 末尾
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # 模块名:app实例名
        host="0.0.0.0",  # 允许外部访问
        port=8002,       # 端口号
        reload=True       # 开发模式下自动重载
    )