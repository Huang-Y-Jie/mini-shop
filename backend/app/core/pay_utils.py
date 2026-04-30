import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime

class PayUtils:
    """支付工具类"""
    
    @staticmethod
    def generate_sign(params: dict, api_key: str) -> str:
        """生成微信支付签名
        
        Args:
            params: 参数字典
            api_key: 微信支付API密钥
            
        Returns:
            str: 签名字符串
        """
        # 按字典序排序
        items = sorted(params.items())
        sign_str = "&"
        for key, value in items:
            sign_str += f"{key}={value}&"
        sign_str += f"key={api_key}"
        # MD5加密
        return hashlib.md5(sign_str.encode()).hexdigest().upper()
    
    @staticmethod
    def build_xml(params: dict) -> str:
        """构建XML格式数据
        
        Args:
            params: 参数字典
            
        Returns:
            str: XML字符串
        """
        xml_data = "<xml>"
        for key, value in params.items():
            xml_data += f"<{key}>{value}</{key}>"
        xml_data += "</xml>"
        return xml_data
    
    @staticmethod
    def parse_xml(xml_data: bytes) -> dict:
        """解析XML数据
        
        Args:
            xml_data: XML字节数据
            
        Returns:
            dict: 解析后的参数字典
        """
        root = ET.fromstring(xml_data)
        params = {}
        for child in root:
            params[child.tag] = child.text
        return params
    
    @staticmethod
    def generate_nonce_str() -> str:
        """生成随机字符串
        
        Returns:
            str: 随机字符串
        """
        return str(int(datetime.now().timestamp() * 1000))
    
    @staticmethod
    def generate_pay_sign(params: dict, api_key: str) -> str:
        """生成支付参数签名（用于小程序前端调起支付）
        
        Args:
            params: 支付参数字典
            api_key: 微信支付API密钥
            
        Returns:
            str: 签名字符串
        """
        # 按字典序排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "&"
        for key, value in sorted_params:
            sign_str += f"{key}={value}&"
        sign_str += f"key={api_key}"
        # MD5加密
        return hashlib.md5(sign_str.encode()).hexdigest().upper()
