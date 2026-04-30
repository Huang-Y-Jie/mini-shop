from fastapi import APIRouter
from .user import router as user_router
from .product import router as product_router
from .cart import router as cart_router
from .order import router as order_router
from .pay import router as pay_router
from .admin import router as admin_router
from .address import router as address_router
from .statistics import router as statistics_router
from .banner import router as banner_router
from .region import router as region_router

# 导出各个路由，供 main.py 直接使用
user = user_router
product = product_router
cart = cart_router
order = order_router
pay = pay_router
admin = admin_router
address = address_router
statistics = statistics_router
banner = banner_router
region = region_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(product_router, prefix="/product", tags=["product"])
api_router.include_router(cart_router, prefix="/cart", tags=["cart"])
api_router.include_router(order_router, prefix="/order", tags=["order"])
api_router.include_router(pay_router, prefix="/pay", tags=["pay"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(address_router, prefix="/address", tags=["address"])
api_router.include_router(statistics_router, prefix="/statistics", tags=["statistics"])
api_router.include_router(banner_router, prefix="/banner", tags=["banner"])
api_router.include_router(region_router, prefix="/region", tags=["region"])
