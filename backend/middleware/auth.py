# backend/middleware/auth.py

from functools import wraps
from flask import g, request, jsonify
import jwt
from datetime import datetime
from backend.models.user import User
from flask import current_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头中获取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': '未提供认证令牌'}), 401
        
        try:
            # 解析令牌
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],  # 确保配置正确
                algorithms=[current_app.config['JWT_ALGORITHM']]
            )
            
            # 获取用户ID
            user_id = payload.get('user_id')
            if not user_id:
                return jsonify({'message': '无效的认证令牌'}), 401
            
            # 从数据库加载用户信息
            user = User.query.get(user_id)
            if not user:
                return jsonify({'message': '用户不存在'}), 404
            
            # 将用户信息存入g对象
            g.current_user = user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的认证令牌'}), 401
        except Exception as e:
            return jsonify({'message': f'认证过程发生错误: {str(e)}'}), 500
        
        return f(*args, **kwargs)
    
    return decorated