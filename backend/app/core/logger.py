import logging
import os
from datetime import datetime

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 创建日志文件
log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(module)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 脱敏函数
def mask_sensitive_data(data):
    if isinstance(data, str):
        # 脱敏手机号
        if len(data) == 11 and data.isdigit():
            return data[:3] + '****' + data[7:]
        # 脱敏交易号
        if len(data) > 10:
            return data[:4] + '****' + data[-4:]
    return data

# 记录日志的函数
def log_action(module, user, action, status, error=''):
    # 脱敏处理
    user = mask_sensitive_data(user)
    if error:
        error = mask_sensitive_data(str(error))
    
    # 记录日志
    extra = {
        'user': user,
        'action': action,
        'status': status,
        'error': error
    }
    logger.info('', extra=extra)
