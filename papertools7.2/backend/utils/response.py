# utils/response.py

def format_response(code=200, message="操作成功", data=None):
    """统一 API 响应格式"""
    return {
        "code": code,
        "message": message,
        "data": data
    }