from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import json
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.bloom_filter import product_bloom_filter
from app.models import Product, Category

router = APIRouter()

"""
商品相关API

包括商品分类、商品列表、商品详情等功能
"""


@router.get("/category/list")
async def get_category_list(db: Session = Depends(get_db)):
    """获取商品分类列表
    
    Returns:
        dict: 分类列表数据
    """
    # 尝试从Redis获取
    redis = get_redis()
    if redis:
        cached_data = redis.get("product:categories")
        if cached_data:
            return {"code": 200, "msg": "success", "data": json.loads(cached_data)}
    
    # 从数据库获取
    categories = db.query(Category).order_by(Category.sort).all()
    
    category_list = []
    for category in categories:
        category_list.append({
            "id": category.id,
            "name": category.name
        })
    
    # 缓存结果
    if redis:
        redis.set("product:categories", json.dumps(category_list), ex=60*60)  # 1小时过期
    
    return {"code": 200, "msg": "success", "data": category_list}

@router.get("/list")
async def get_product_list(category_id: int = None, keyword: str = None, page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    """获取商品列表
    
    Args:
        category_id: 分类ID，可选
        keyword: 搜索关键词，可选
        page: 页码，默认1
        size: 每页数量，默认10
        db: 数据库会话
        
    Returns:
        dict: 商品列表和总数
    """
    try:
        print("开始执行商品列表API")
        # 构建缓存键
        cache_key = f"product:list:{category_id or 'all'}:{keyword or 'none'}:{page}:{size}"
        print(f"缓存键: {cache_key}")
        
        # 尝试从Redis获取
        print("尝试获取Redis连接")
        redis = get_redis()
        print(f"Redis连接: {redis}")
        if redis:
            print("从Redis获取缓存")
            cached_data = redis.get(cache_key)
            if cached_data:
                print("从缓存返回数据")
                return {"code": 200, "msg": "success", "data": json.loads(cached_data)}
        
        # 从数据库获取
        print("从数据库获取数据")
        query = db.query(Product).filter(Product.status == 1)
        print(f"查询对象: {query}")
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
            print(f"添加分类过滤: {category_id}")
        
        if keyword:
            query = query.filter(Product.name.like(f"%{keyword}%"))
            print(f"添加关键词过滤: {keyword}")
        
        print("计算总数")
        total = query.count()
        print(f"总数: {total}")
        
        print("获取商品列表")
        products = query.offset((page - 1) * size).limit(size).all()
        print(f"商品数量: {len(products)}")
        
        product_list = []
        for product in products:
            product_list.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "cover_img": product.cover_img,
                "sales": product.sales
            })
        
        result = {"list": product_list, "total": total}
        print(f"结果: {result}")
        
        # 缓存结果
        if redis:
            print("缓存结果")
            redis.set(cache_key, json.dumps(result), ex=10*60)  # 10分钟过期
        
        print("返回结果")
        return {"code": 200, "msg": "success", "data": result}
    except Exception as e:
        print(f"商品列表API错误: {e}")
        import traceback
        print(traceback.format_exc())
        raise

@router.get("/detail/{id}")
async def get_product_detail(id: int, db: Session = Depends(get_db)):
    """获取商品详情
    
    Args:
        id: 商品ID
        db: 数据库会话
        
    Returns:
        dict: 商品详细信息
        
    Raises:
        HTTPException: 商品不存在时抛出404异常
    """
    # 使用布隆过滤器检查商品是否可能存在
    if not product_bloom_filter.contains(str(id)):
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 先从Redis获取商品详情
    redis = get_redis()
    if redis:
        product_data = redis.get(f"product:detail:{id}")
        
        if product_data:
            product_info = json.loads(product_data)
            return {"code": 200, "msg": "success", "data": product_info}
    
    # 从数据库获取
    product = db.query(Product).filter(Product.id == id, Product.status == 1).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    product_info = {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "desc": product.desc,
        "cover_img": product.cover_img,
        "imgs": json.loads(product.imgs) if product.imgs else [],
        "status": product.status,
        "sales": product.sales
    }
    
    # 更新Redis缓存
    if redis:
        redis.set(f"product:detail:{id}", json.dumps(product_info), ex=30*60)  # 30分钟过期
    
    return {"code": 200, "msg": "success", "data": product_info}
