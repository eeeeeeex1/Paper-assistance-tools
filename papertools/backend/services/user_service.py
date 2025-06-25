# backend/app/services/user_service.py
from flask import current_app
from backend.models import User  # 而不是 from backend.models.user import User # 导入 User 模型
from backend.config.database import db     # 导入数据库实例
import hashlib
import jwt
from datetime import datetime, timedelta

class UserService:
    def get_user_by_id(self, user_id):
        """通过 ID 获取用户"""
        return User.query.get(user_id)
    
    def get_user_by_username(self, username):
        """通过用户名获取用户"""
        return User.query.filter_by(username=username).first()
    
    def create_user(self, username, password, email):
        """创建新用户"""
        # 检查用户名是否已存在
        if self.get_user_by_username(username):
            return None, "用户名已存在"
        
        # 密码加密
        hashed_password = self._hash_password(password)
        
        # 创建用户对象
        new_user = User(
            username=username,
            password=hashed_password,
            email=email,
            created_at=datetime.utcnow()
        )
        
        # 保存到数据库
        db.session.add(new_user)
        db.session.commit()
        
        return new_user, None
    
    def verify_password(self, password, hashed_password):
        """验证密码"""
        return hashed_password == self._hash_password(password)
    
    def generate_token(self, user_id, username):
        """生成 JWT Token"""
        # 设置 Token 有效期（例如 24 小时）
        expires_in = timedelta(hours=24)
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + expires_in
        }
        
        # 使用应用的 SECRET_KEY 签名 Token
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return token
    
    def update_user_info(self, user_id, **kwargs):
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        # 更新允许修改的字段
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ['id', 'password']:
                setattr(user, key, value)
        
        # 如果需要更新密码，单独处理
        if 'password' in kwargs:
            user.password = self._hash_password(kwargs['password'])
        
        # 提交更改
        db.session.commit()
        return True, "更新成功"
    
    def delete_user(self, user_id):
        """删除用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        db.session.delete(user)
        db.session.commit()
        return True, "删除成功"
    
    # 辅助方法：密码加密
    def _hash_password(self, password):
        """SHA256 密码加密"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()