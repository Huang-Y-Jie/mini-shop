from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import asyncio
import time
from .redis import get_redis

router = APIRouter()

# 存储WebSocket连接
active_connections: Dict[int, WebSocket] = {}
# 存储连接状态
connection_status: Dict[int, dict] = {}
# 最大重连次数
MAX_RECONNECT_ATTEMPTS = 3
# 重连间隔（秒）
RECONNECT_INTERVAL = 5

@router.websocket("/ws/admin/order")
async def websocket_endpoint(websocket: WebSocket, admin_token: str = Query(...), reconnect_attempt: int = Query(0)):
    await websocket.accept()
    
    admin_id = None
    try:
        # 验证token
        from .auth import decode_token
        payload = decode_token(admin_token)
        admin_id = int(payload.get("sub"))
        
        # 存储连接
        active_connections[admin_id] = websocket
        
        # 存储连接状态
        connection_status[admin_id] = {
            "last_activity": time.time(),
            "reconnect_attempts": 0,
            "connected": True
        }
        
        # 存储到Redis
        redis = get_redis()
        if redis:
            redis.sadd("admin:ws:clients", admin_id)
        
        # 心跳检测任务
        async def heartbeat():
            while True:
                try:
                    await websocket.send_json({"type": "ping"})
                    await asyncio.sleep(30)  # 每30秒发送一次心跳
                except:
                    break
        
        # 启动心跳检测
        heartbeat_task = asyncio.create_task(heartbeat())
        
        # 处理消息
        while True:
            data = await websocket.receive_text()
            # 更新最后活动时间
            connection_status[admin_id]["last_activity"] = time.time()
            # 处理心跳响应
            if data == "pong":
                continue
            # 处理重连请求
            if data == "reconnect":
                await websocket.send_json({"type": "reconnect_success"})
                continue
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        # 处理重连逻辑
        if admin_id and connection_status.get(admin_id, {}).get("reconnect_attempts", 0) < MAX_RECONNECT_ATTEMPTS:
            print(f"尝试重连 admin_id: {admin_id}")
            connection_status[admin_id]["reconnect_attempts"] += 1
            connection_status[admin_id]["connected"] = False
    finally:
        # 清理连接
        if admin_id in active_connections:
            del active_connections[admin_id]
        if admin_id in connection_status:
            del connection_status[admin_id]
        # 从Redis中移除
        redis = get_redis()
        if redis:
            redis.srem("admin:ws:clients", admin_id)
        await websocket.close()

# 广播消息
def broadcast_message(message: dict):
    """广播消息给所有在线管理员"""
    print(f"开始广播消息: {message['type']}")
    admin_ids = []
    
    # 从Redis获取在线管理员ID
    redis = get_redis()
    if redis:
        try:
            admin_ids = redis.smembers("admin:ws:clients")
            # 转换为整数
            admin_ids = [int(admin_id.decode('utf-8')) for admin_id in admin_ids]
            print(f"从Redis获取到的管理员ID: {admin_ids}")
        except Exception as e:
            print(f"从Redis获取管理员ID失败: {e}")
            pass
    
    # 从active_connections中获取，确保不遗漏
    active_admin_ids = list(active_connections.keys())
    print(f"从active_connections获取到的管理员ID: {active_admin_ids}")
    admin_ids = list(set(admin_ids + active_admin_ids))
    print(f"最终要广播的管理员ID: {admin_ids}")
    
    for admin_id in admin_ids:
        if admin_id in active_connections:
            try:
                import asyncio
                asyncio.create_task(active_connections[admin_id].send_json(message))
                print(f"成功向管理员 {admin_id} 广播消息")
            except Exception as e:
                print(f"Broadcast error: {e}")
                # 标记连接为断开
                if admin_id in connection_status:
                    connection_status[admin_id]["connected"] = False

# 清理无效连接
def cleanup_inactive_connections():
    """清理长时间不活跃的连接"""
    current_time = time.time()
    inactive_admins = []
    
    for admin_id, status in connection_status.items():
        if current_time - status.get("last_activity", 0) > 300:  # 5分钟不活跃
            inactive_admins.append(admin_id)
    
    for admin_id in inactive_admins:
        if admin_id in active_connections:
            del active_connections[admin_id]
        if admin_id in connection_status:
            del connection_status[admin_id]
        # 从Redis中移除
        redis = get_redis()
        if redis:
            redis.srem("admin:ws:clients", admin_id)

# 启动连接清理任务
async def start_connection_cleanup():
    """定期清理无效连接"""
    while True:
        try:
            cleanup_inactive_connections()
        except Exception as e:
            print(f"清理连接失败: {e}")
        await asyncio.sleep(60)  # 每分钟清理一次