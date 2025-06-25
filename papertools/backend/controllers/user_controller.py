# backend/controllers/user_controller.py
from flask import current_app
from services.user_service import UserService

class UserController:
    def __init__(self):
        self.user_service = UserService()
    
    def register(self, username, password, email):
        """用户注册处理"""
        # 调用服务层创建用户
        user, error = self.user_service.create_user(username, password, email)
        
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
    
    def login(self, username, password):
        """用户登录处理"""
        # 获取用户
        user = self.user_service.get_user_by_username(username)
        
        if not user:
            return {
                'code': 404,
                'message': '用户不存在'
            }
        
        # 验证密码
        if not self.user_service.verify_password(password, user.password):
            return {
                'code': 401,
                'message': '密码错误'
            }
        
        # 生成 Token
        token = self.user_service.generate_token(user.id, user.username)
        
        return {
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': token,
                'user_info': user.to_dict()
            }
        }
    
    def get_user_info(self, user_id):
        """获取用户信息"""
        user = self.user_service.get_user_by_id(user_id)
        
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
        success, message = self.user_service.update_user_info(user_id, **kwargs)
        
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
        success, message = self.user_service.delete_user(user_id)
        
        if not success:
            return {
                'code': 400,
                'message': message
            }
        
        return {
            'code': 200,
            'message': message
        }