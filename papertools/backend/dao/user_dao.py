from flask import current_app
from backend.models.user import User  # 导入 User 模型
from backend.config.database import db  # 导入数据库实例
import hashlib
import jwt
from datetime import datetime, timedelta,timezone 
import logging
import bcrypt
from config.logging_config import logger
from typing import Optional
from typing import Dict, Any

#------------------------------------------
from typing import List, Dict, Any,Optional
from sqlalchemy.exc import SQLAlchemyError
#-----------------------------------------
# 初始化日志记录器
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class UserDao:
    def get_user_by_id(self, user_id):
        """通过 ID 获取用户"""
        return User.query.get(user_id)

    def get_user_by_identity(self, identity):
        """通过用户名获取用户"""
        logger.info(f"check user")
    
        return User.query.filter(
            (User.username == identity) | (User.email == identity) |(User.id == identity)
        ).first()

    def create_user(self, username, password, email):
        """创建新用户"""
        # 检查用户名是否已存在
        logger.info(f"make new user: {username}")

        # 创建用户对象，设置 permission 为 7
        new_user = User(
            username=username,
            password_hash=password,
            email=email,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            permission=7  # 设置默认 permission 为 7
        )
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"new user has been created,waiting for writing")
        created_user = User.query.filter_by(username=username).first()
        if created_user:
            # 记录用户创建成功及详细信息（排除敏感字段）
            logger.info(f"用户创建成功: ID={created_user.id}, 用户名={created_user.username}, 邮箱={created_user.email}, 权限={created_user.permission}")
            return created_user, None
        return new_user, None

    def verify_password(self, plain_password: str, stored_password: str) -> bool:
        return plain_password == stored_password  # 直接字符串比较

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
#保存
    def save_user(self, user):
        """保存用户到数据库（新增或更新）"""
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_user(self, user_id):
        """删除用户"""
        try:
            # 检查用户是否存在
            user = User.query.get(user_id)
            if not user:
                return False, "用户不存在"

            db.session.delete(user)
            db.session.commit()
            return True, "删除成功"
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除用户失败: {str(e)}")
            return False, f"删除用户失败: {str(e)}"

    # 辅助方法：密码加密
    def hash_password(self, plain_password: str) -> str:
        return plain_password  # 直接返回明文
    
    #-------------------------------------------------------------------------------
    # dao/user_dao.py
    def get_all_user(
        self,
        page: int = 1,
        per_page: int = 10,
        filter_username: Optional[str] = None,
        include_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        获取分页用户数据
        :param include_sensitive: 是否包含敏感信息
        :param page: 页码
        :param per_page: 每页数量
        :param filter_username: 按用户名过滤
        :return: 包含分页信息的字典
        """
        try:
            logger.info(f"Dao get all user")
            query = User.query
            
            if filter_username:
                query = query.filter(User.username.like(f"%{filter_username}%"))
            
            paginated_users = query.paginate(page=page, per_page=per_page, error_out=False)
            logger.info('Dao get all user success')
            return {
                'items': [user.to_dict(include_sensitive) for user in paginated_users.items],
                'total': paginated_users.total,
                'pages': paginated_users.pages,
                'current_page': page,
                'per_page': per_page
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
#lmk--------------------------------------------------------------------
    def get_total_user_count(self):
            """获取用户的总数量"""
            return User.query.count()
#lmk----------------------------------------------------------
    @staticmethod
    def get_weekly_login_count():
        """使用updated_at字段统计近7天登录用户数"""
        end_date = datetime.utcnow().date()
        date_range = [end_date - timedelta(days=i) for i in range(6, -1, -1)]
        date_strings = [d.strftime('%Y-%m-%d') for d in date_range]
        
        daily_counts = []
        for date in date_range:
            start_time = datetime.combine(date, datetime.min.time())
            end_time = datetime.combine(date, datetime.max.time())
            
            # 使用updated_at字段统计
            count = User.query.filter(
                User.updated_at.between(start_time, end_time)
            ).count()
            
            daily_counts.append(count)
        
        return {
            'dates': date_strings,
            'counts': daily_counts
        }