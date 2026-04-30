from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "测试API服务运行中"}

@app.get("/test")
def test():
    return {"code": 200, "msg": "success", "data": {"message": "测试成功"}}

@app.get("/api/product/list")
def product_list():
    return {"code": 200, "msg": "success", "data": {"list": [], "total": 0}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "test_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
