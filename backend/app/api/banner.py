from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Banner
from app.core.auth import verify_admin_token
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class BannerCreate(BaseModel):
    title: str
    subtitle: str
    image: str
    link: Optional[str] = None
    sort: Optional[int] = 0
    status: Optional[bool] = True

class BannerUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    image: Optional[str] = None
    link: Optional[str] = None
    sort: Optional[int] = None
    status: Optional[bool] = None

@router.get("/list")
async def get_banners(db: Session = Depends(get_db)):
    """获取轮播图列表"""
    try:
        banners = db.query(Banner).filter_by(status=True).order_by(Banner.sort.asc()).all()
        banner_list = [banner.to_dict() for banner in banners]
        return {
            'code': 200,
            'message': '获取轮播图列表成功',
            'data': banner_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'获取轮播图列表失败: {str(e)}')

@router.get("/admin/list")
async def get_admin_banners(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin = Depends(verify_admin_token)
):
    """获取轮播图列表（管理后台）"""
    try:
        total = db.query(Banner).count()
        banners = db.query(Banner).order_by(Banner.sort.asc(), Banner.id.desc()).offset((page - 1) * size).limit(size).all()
        banner_list = [banner.to_dict() for banner in banners]
        
        return {
            'code': 200,
            'message': '获取轮播图列表成功',
            'data': {
                'list': banner_list,
                'total': total,
                'page': page,
                'size': size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'获取轮播图列表失败: {str(e)}')

@router.post("/admin/add")
async def add_banner(
    banner_data: BannerCreate = Body(...),
    db: Session = Depends(get_db),
    current_admin = Depends(verify_admin_token)
):
    """添加轮播图"""
    try:
        if not banner_data.title or not banner_data.subtitle or not banner_data.image or banner_data.image.strip() == '':
            raise HTTPException(status_code=400, detail='标题、副标题和图片不能为空')
        
        banner = Banner(
            title=banner_data.title,
            subtitle=banner_data.subtitle,
            image=banner_data.image,
            link=banner_data.link,
            sort=banner_data.sort,
            status=banner_data.status
        )
        
        db.add(banner)
        db.commit()
        db.refresh(banner)
        
        return {
            'code': 200,
            'message': '添加轮播图成功',
            'data': banner.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'添加轮播图失败: {str(e)}')

@router.put("/admin/update/{banner_id}")
async def update_banner(
    banner_id: int,
    banner_data: BannerUpdate = Body(...),
    db: Session = Depends(get_db),
    current_admin = Depends(verify_admin_token)
):
    """更新轮播图"""
    try:
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            raise HTTPException(status_code=404, detail='轮播图不存在')
        
        if banner_data.title is not None:
            banner.title = banner_data.title
        if banner_data.subtitle is not None:
            banner.subtitle = banner_data.subtitle
        if banner_data.image is not None:
            banner.image = banner_data.image
        if banner_data.link is not None:
            banner.link = banner_data.link
        if banner_data.sort is not None:
            banner.sort = banner_data.sort
        if banner_data.status is not None:
            banner.status = banner_data.status
        
        db.commit()
        db.refresh(banner)
        
        return {
            'code': 200,
            'message': '更新轮播图成功',
            'data': banner.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'更新轮播图失败: {str(e)}')

@router.delete("/admin/delete/{banner_id}")
async def delete_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(verify_admin_token)
):
    """删除轮播图"""
    try:
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            raise HTTPException(status_code=404, detail='轮播图不存在')
        
        db.delete(banner)
        db.commit()
        
        return {
            'code': 200,
            'message': '删除轮播图成功'
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'删除轮播图失败: {str(e)}')
