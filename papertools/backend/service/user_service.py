# backend/controllers/user_controller.py
from flask import current_app
from dao.user_dao import UserDao
from config.logging_config import logger
import bcrypt
from datetime import datetime, timedelta,timezone 
from backend.config.database import db
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from models.user import User
#----------------------------------------------
from sqlalchemy.exc import SQLAlchemyError
#---------------------------------------------
class UserService:
    def __init__(self):
        self.user_dao = UserDao()
    
    def register(self, username, password, email):
        """用户注册处理"""
        # 调用服务层创建用户
        logger.info(f"user_service use rgister")
        hashed_password = password
        user, error = self.user_dao.create_user(username,hashed_password, email)
        
        if error:
            return {
                'code': 400,
                'message': error
            }
        
        return {
            'code': 201,
            'message': '注册成功',
            'data': {
                'user_id': user.id,
                'username': user.username
            }
        }
    
    
    def login(self, email, password):
        """用户登录处理"""
        # 获取用户
        user = self.user_dao.get_user_by_identity(email)
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()#单独处理更新最后登录时间
        logger.info(f"更新最后登录时间: {user.updated_at}")
         # 使用OR条件查询username或email匹配的用户

        if not user:
            logger.warning(f"登录失败：用户不存在 - {email}")
            return {
                'code': 401,
                'message': '用户名或密码错误'
            }
        
        # 验证密码
        if not self.user_dao.verify_password(password, user.password_hash):
            logger.warning(f"登录失败：密码错误 - 用户: {user.username}")
            return {
                'code': 401,
                'message': '用户名或密码错误'
            }
        
        # 生成 Token
        token = self.user_dao.generate_token(user.id, user.username)
        
        logger.info(f"登录成功 - 用户: {user.username}")

        # 返回用户信息字典，而非整个对象
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    
    def get_user_info(self, identity):
        """获取用户信息"""
        user = self.user_dao.get_user_by_identity(identity)
        
        if not user:
            return {
                'code': 404,
                'message': '用户不存在'
            }
        
        return {
            'code': 200,
            'message': '获取成功',
            'data': user.to_dict()
        }
    
    def update_user(self, user_id, **kwargs):
        """更新用户信息"""
        success, message = self.user_dao.update_user_info(user_id, **kwargs)
        
        if not success:
            return {
                'code': 400,
                'message': message
            }
        
        return {
            'code': 200,
            'message': message
        }
    
    def delete_user(self, user_id):
        """删除用户"""
        success, message = self.user_dao.delete_user(user_id)
        
        if not success:
            return {
                'code': 400,
                'message': message
            }
        
        return {
            'code': 200,
            'message': message
        }
    #---------------------------------------------------------------------------------------------------------
    def get_all_users(
        self,  # 添加self参数
        page: int = 1,
        per_page: int = 10,
        filter_username: Optional[str] = None,
        include_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        获取用户列表（支持分页和过滤）
        :param include_sensitive: 是否包含敏感信息
        :param page: 页码
        :param per_page: 每页数量
        :param filter_username: 按用户名过滤（可选）
        :return: 包含用户列表、总页数、总数量的字典
        """
        try:
            logger.info('Calling DAO layer to get all users')
            result = self.user_dao.get_all_user(  # 使用self.user_dao
                include_sensitive=include_sensitive,
                page=page,
                per_page=per_page,
                filter_username=filter_username
            )
            logger.info(f"service get_all_users result: {result}")
            return result
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"获取用户列表失败: {str(e)}")
            raise ValueError(f"数据库操作失败: {str(e)}")
        except Exception as e:
            logger.error(f"获取用户列表异常: {str(e)}")
            raise ValueError(f"获取用户列表失败: {str(e)}")