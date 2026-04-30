from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import redis

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

async def redis_exception_handler(request: Request, exc: redis.RedisError):
    # Redis异常处理，返回503服务降级
    return JSONResponse(
        status_code=503,
        content={"code": 503, "msg": "服务临时降级", "data": None}
    )

async def general_exception_handler(request: Request, exc: Exception):
    # 通用异常处理
    import traceback
    print(f"服务器内部错误: {exc}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"code": 500, "msg": "服务器内部错误", "data": None}
    )
