# backend/app/models/user.py
from backend.config.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func  # 导入 func 对象

from backend.models.paper import Paper
from backend.models.operation import Operation

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}  # 支持表结构扩展
    
    # 基本字段定义
    id = db.Column(
        db.Integer,
        primary_key=True
    )  # 使用 BigInteger 对应数据库 BIGINT
    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )
    password_hash = db.Column(
        db.String(100),
        nullable=False
    )  # 重命名为 password_hash
    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        server_default=func.now()
    )
    updated_at = db.Column(
        db.DateTime, 
        server_default=func.now(),
        onupdate=func.now()
    )

    # 密码相关方法
    def set_password(self, password):
        """设置加密密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    # 对象转字典（用于 API 响应）
    def to_dict(self, include_sensitive=False):
        """
        将用户对象转换为字典
        :param include_sensitive: 是否包含敏感信息
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        if include_sensitive:
            data['created_at_utc'] = self.created_at
            data['updated_at_utc'] = self.updated_at
        return data
    
    # 静态方法：通过用户名查询用户
    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    
    # 静态方法：通过邮箱查询用户
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()