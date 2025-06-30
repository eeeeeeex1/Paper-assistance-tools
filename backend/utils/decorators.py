# backend/utils/decorators.py
from functools import wraps
from datetime import datetime
from pytz import timezone

BEIJING_TZ = timezone('Asia/Shanghai')

def convert_to_beijing(func):
    """将函数返回的 datetime 转换为北京时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        if isinstance(result, datetime):
            return result.astimezone(BEIJING_TZ)
        
        if isinstance(result, list) and all(isinstance(item, datetime) for item in result):
            return [item.astimezone(BEIJING_TZ) for item in result]
        
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, datetime):
                    result[key] = value.astimezone(BEIJING_TZ)
            return result
            
        return result
    
    return wrapper