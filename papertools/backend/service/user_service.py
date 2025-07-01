# backend/controllers/user_controller.py
from flask import current_app
from dao.user_dao import UserDao
from backend.dao.operation_dao import Operation
from config.logging_config import logger
import bcrypt
from datetime import datetime, timedelta,timezone 
from backend.config.database import db
from backend.models.user import User
from backend.models.operation import Operation
from flask import jsonify  # 添加导入
from utils.response import format_response

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
        # 登录成功后记录操作
        #Operation.log_operation(
        #   user_id=user.id,
        #    paper_id=None,
        #    operation_type="login",
        #    file_name="登录"
        #)
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
    
#更新用户信息，新增时间
    def update_user(self, user_data):
        """
        更新用户信息
        :param user_data: 用户数据字典或 User 模型实例
        :return: 更新结果
        """
        try:
            # 1. 从数据库获取原始用户对象（确保数据一致性）
            user_id = user_data.get('id') if isinstance(user_data, dict) else user_data.id
            user = self.user_dao.get_user_by_id(user_id)
            
            if not user:
                return jsonify(code=404, message="用户不存在")
            
            # 2. 更新用户字段（根据需要选择性更新）
            if isinstance(user_data, dict):
                # 更新基本信息
                if 'username' in user_data:
                    user.username = user_data['username']
                if 'email' in user_data:
                    user.email = user_data['email']
                
                # 【关键】更新最后登录时间
                if 'last_login' in user_data:
                    user.last_login = user_data['last_login']
                
                # 处理密码更新（如果有）
                if 'password_hash' in user_data:
                    # 假设传入的是已加密的密码
                    user.password_hash = user_data['password_hash']
                
                # 更新时间戳
                user.updated_at = datetime.utcnow()
            
            else:  # 如果传入的是 User 模型实例
                # 直接用传入的实例更新数据库（需确保实例已被修改）
                pass
            
            # 3. 持久化到数据库
            updated_user = self.user_dao.save_user(user)
            
            return jsonify({
                "code": 200,
                "message": "用户信息更新成功",
                "data": updated_user.to_dict() if hasattr(updated_user, 'to_dict') else None
            }), 200
            
        except Exception as e:
            return jsonify({
                "code": 500,
                "message": f"更新用户失败: {str(e)}"
            }), 500
        
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

def get_user_operations(self, user_id, page=1, per_page=20):
        """获取用户的操作记录"""
        # 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            return format_response(code=404, message="用户不存在")
        
        # 正确调用 DAO 方法并接收分页对象
        operations_paginated = self.operation_dao.get_user_operations(
            user_id, page, per_page
        )
        
         # 格式化响应数据
        operations = [op.to_dict() for op in operations_paginated.items]
        return format_response(
            code=200,
            message="获取成功",
            data={
                'user_info': user.to_dict(),
                'operations': operations,
                'total': operations_paginated.total,
                'pages': operations_paginated.pages,
                'current_page': operations_paginated.page
            }
        )