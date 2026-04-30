from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import create_user_token, verify_user_token
from app.core.redis import get_redis
from app.core.logger import log_action
from app.models import User
import json

router = APIRouter()

from pydantic import BaseModel

class AuthRequest(BaseModel):
    code: str

@router.post("/auth")
async def user_auth(request: AuthRequest, db: Session = Depends(get_db)):
    code = request.code
    try:
        print(f"Received code: {code}")
        # 调用微信API获取openid
        import requests
        from app.core.config import settings
        
        # 微信小程序登录API
        wx_api_url = f"https://api.weixin.qq.com/sns/jscode2session?appid={settings.WX_APPID}&secret={settings.WX_APPSECRET}&js_code={code}&grant_type=authorization_code"
        
        # 发送请求到微信API
        response = requests.get(wx_api_url)
        wx_data = response.json()
        
        # 检查是否获取成功
        if "openid" in wx_data:
            openid = wx_data["openid"]
            print(f"Got openid: {openid}")
        else:
            # 如果获取失败，抛出异常
            print(f"Failed to get openid from WeChat API: {wx_data}")
            raise HTTPException(status_code=400, detail="获取openid失败")
        
        # 查找用户
        user = db.query(User).filter(User.openid == openid).first()
        if not user:
            # 创建新用户
            user = User(openid=openid)
            db.add(user)
            db.commit()
            db.refresh(user)
            log_action("user", openid, "register", "success")
        else:
            log_action("user", openid, "login", "success")
        
        # 生成token
        token = create_user_token(user.id)
        return {"code": 200, "msg": "success", "data": {"token": token, "user_id": user.id}}
    except Exception as e:
        log_action("user", "unknown", "login", "fail", str(e))
        # 如果发生错误，抛出异常
        raise HTTPException(status_code=500, detail="登录失败")

@router.get("/info")
async def get_user_info(current_user: User = Depends(verify_user_token)):
    return {"code": 200, "msg": "success", "data": {"nickname": current_user.nickname or "用户", "phone": current_user.phone, "address": current_user.address, "openid": current_user.openid}}

@router.put("/info")
async def update_user_info(request: dict, current_user: User = Depends(verify_user_token), db: Session = Depends(get_db)):
    if request.get("nickname"):
        current_user.nickname = request.get("nickname")
    if request.get("phone"):
        current_user.phone = request.get("phone")
    if request.get("address"):
        current_user.address = request.get("address")
    db.commit()
    return {"code": 200, "msg": "修改成功", "data": None}

@router.post("/logout")
async def user_logout(current_user: User = Depends(verify_user_token)):
    # 删除Redis中的Token
    redis = get_redis()
    if redis:
        redis.delete(f"user:token:{current_user.id}")
    return {"code": 200, "msg": "退出成功", "data": None}
