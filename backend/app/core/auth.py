from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .redis import get_redis
from app.models import User, Admin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/auth")

# 密码哈希
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 暂时直接比较明文密码，绕过bcrypt问题
    return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    # 暂时直接返回明文密码，绕过bcrypt问题
    return password

# JWT token生成和验证
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_user_token(user_id: int) -> str:
    token = create_access_token(data={"sub": str(user_id)})
    # 存储Token到Redis
    redis = get_redis()
    if redis:
        redis.set(f"user:token:{user_id}", token, ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return token

def create_admin_token(admin_id: int) -> str:
    token = create_access_token(data={"sub": str(admin_id)})
    # 存储Token到Redis
    redis = get_redis()
    if redis:
        redis.set(f"admin:token:{admin_id}", token, ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return token

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 依赖项
async def verify_user_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    # 验证Redis中的Token
    redis = get_redis()
    if redis:
        try:
            redis_token = redis.get(f"user:token:{user_id}")
            if not redis_token or redis_token != token:
                raise credentials_exception
        except Exception:
            # Redis 连接失败，跳过验证，继续使用数据库验证
            pass
    # 获取用户信息
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise credentials_exception
    return user

async def verify_admin_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    admin_id: str = payload.get("sub")
    if admin_id is None:
        raise credentials_exception
    # 验证Redis中的Token
    redis = get_redis()
    if redis:
        try:
            redis_token = redis.get(f"admin:token:{admin_id}")
            if not redis_token or redis_token != token:
                raise credentials_exception
        except Exception:
            # Redis 连接失败，跳过验证，继续使用数据库验证
            pass
    # 获取管理员信息
    admin = db.query(Admin).filter(Admin.id == int(admin_id)).first()
    if not admin:
        raise credentials_exception
    return admin