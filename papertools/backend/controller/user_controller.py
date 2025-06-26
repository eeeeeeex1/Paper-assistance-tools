# backend/app/routes/user_route.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from , SwaggerView
from marshmallow import Schema,fields  # 从marshmallow导入字段
from service.user_service import UserService
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import re
from functools import wraps
import os

user_bp = Blueprint('user', __name__, url_prefix='/api/user')
user_service = UserService()

# JWT认证装饰器zdef token_required(f):
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从请求头中获取Token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'message': '缺少Token',
                'error_code': 401
            }), 401
        
        try:
            # 使用配置的密钥解码Token
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=[current_app.config['JWT_ALGORITHM']]
            )
            # 将用户ID添加到请求上下文中
            request.current_user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({
                'message': 'Token已过期',
                'error_code': 401
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'message': '无效的Token',
                'error_code': 401
            }), 401
        
        return f(*args, **kwargs)
    return decorated

# 验证邮箱格式
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

# 验证密码强度
def is_strong_password(password):
    # 至少8位，包含大小写字母和数字
    return len(password) >= 8 #and \
        #any(c.isupper() for c in password) and \
        #any(c.islower() for c in password) and \
        #any(c.isdigit() for c in password)

# 用户注册接口
@user_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['用户管理'],
    'summary': '用户注册',
    'description': '创建新用户账号，需要提供用户名、密码和邮箱',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['username', 'password', 'email'],
                'properties': {
                    'username': {
                        'type': 'string', 
                        'description': '用户名,长度4-20字符', 
                        'example': 'testuser',
                        'minLength': 4,
                        'maxLength': 20
                    },
                    'password': {
                        'type': 'string', 
                        'description': '密码至少8位,包含大小写字母和数字', 
                        'example': 'SecurePass123',
                        'minLength': 8
                    },
                    'email': {
                        'type': 'string', 
                        'description': '有效邮箱地址', 
                        'example': 'user@example.com'
                    },
                    'phone': {
                        'type': 'string', 
                        'description': '可选，手机号码', 
                        'example': '13800138000'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': '注册成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': '注册成功'},
                    'user_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': '参数错误', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': '服务器内部错误'}
    }
    },
)
def register():
    data = request.get_json()
    # 数据验证
    if not data:
        return jsonify({
            'message': '请求数据为空',
            'error_code': 400
        }), 400

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')


    # 加密密码
    hashed_password = generate_password_hash(password)
    
    # 调用控制器处理注册
    result = user_service.register({
        'username': username,
        'password': hashed_password,
        'email': email
    })
    
    if result.get('success'):
        return jsonify({
            'message': '用户注册成功',
            'user_id': result.get('user_id'),
            'username': username
        }), 201
    else:
        error_code = 409 if result.get('message') == '用户已存在' else 500
        return jsonify({
            'message': result.get('message', '注册失败'),
            'error_code': error_code
        }), error_code

# 用户登录接口
@user_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['用户管理'],
    'summary': '用户登录',
    'description': '用户登录并获取JWT访问令牌',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['identity', 'password'],
                'properties': {
                    'identity': {
                        'type': 'string', 
                        'description': '账号（用户名或邮箱）', 
                        'example': 'admin'
                    },
                    'password': {
                        'type': 'string', 
                        'description': '密码', 
                        'example': 'SecurePass123'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': '登录成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': '登录成功'},
                    'token': {'type': 'string', 'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'},
                    'user_info': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'account': {'type': 'string', 'example': 'admin'},
                            'name': {'type': 'string', 'example': '管理员'},
                            'role': {'type': 'string', 'example': 'admin'}
                        }
                    }
                }
            }
        },
        401: {
            'description': '认证失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': False},
                    'message': {'type': 'string', 'example': '账号或密码错误'}
                }
            }
        },
        500: {'description': '服务器内部错误'}
    }
    }
)
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'message': '请求数据为空',
                'error_code': 400
            }), 400
        
        identity = data.get('identity')
        password = data.get('password')
        
        if not all([identity, password]):
            return jsonify({
                'message': '缺少必要参数',
                'error_code': 400
            }), 400
        
        # 调用控制器验证用户
        user = user_service.login(identity, password)
        
        if not user:
            return jsonify({
                'message': '账号或密码错误',
                'error_code': 401
            }), 401
        
        # 生成JWT Token
        expires = timedelta(hours=current_app.config.get('JWT_EXPIRE_HOURS', 1))
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + expires
        }
        token = jwt.encode(
            payload, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithm=current_app.config['JWT_ALGORITHM']
        )
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': token,
            'expires_in': int(expires.total_seconds()),
            'user_info': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'created_at': user['created_at'].isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'登录错误: {str(e)}')
        return jsonify({
            'message': '登录失败，请稍后再试',
            'error_code': 500
        }), 500

# 获取用户信息接口
@user_bp.route('/info', methods=['GET'])
@token_required  # 使用JWT认证装饰器
@swag_from({
    'tags': ['用户管理'],
    'summary': '获取用户信息',
    'description': '获取当前登录用户的详细信息,需要有效的JWT Token',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT Token(格式:Bearer {token})',
            'example': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        }
    ],
    'responses': {
        200: {
            'description': '用户信息',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'username': {'type': 'string', 'example': 'testuser'},
                    'email': {'type': 'string', 'example': 'user@example.com'}
                }
            }
        },
        401: {
            'description': '未授权',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': '无效的Token'}
                }
            }
        },
        403: {'description': '权限不足'},
        500: {'description': '服务器内部错误'}
    }
})
def get_user_info():
    try:
        user_id = request.current_user_id
        if not user_id:
            return jsonify({
                'message': '用户ID不存在',
                'error_code': 401
            }), 401
        
        # 调用控制器获取用户信息
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'message': '用户不存在',
                'error_code': 404
            }), 404
        
        # 更新最后登录时间
        user_service.update_last_login(user_id)
        
        # 格式化日期时间
        user['created_at'] = user['created_at'].isoformat()
        user['last_login'] = user['last_login'].isoformat() if user['last_login'] else None
        
        return jsonify(user), 200
        
    except Exception as e:
        current_app.logger.error(f'获取用户信息错误: {str(e)}')
        return jsonify({
            'message': '获取用户信息失败，请稍后再试',
            'error_code': 500
        }), 500
    
#示例4：删除用户
@user_bp.route('/<int:user_id>', methods=['DELETE'])
@swag_from({
    'tags': ['用户管理'],
    'summary': '删除用户',
    'description': '删除指定ID的用户账号,需要管理员操作',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': '要删除的用户ID',
            'example': 1001
        },
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT Token(格式:Bearer {token})',
            'example': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        }
    ],
    'responses': {
        200: {
            'description': '用户删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': '用户已成功删除'}
                }
            }
        },
        401: {
            'description': '未授权',
        },
        403: {'description': '权限不足'},
        404: {
            'description': '用户不存在',
        },
        500: {'description': '服务器内部错误'}
    }
})
def delete_user(user_id):
    try:
        # 验证用户ID是否合法
        if not isinstance(user_id, int) or user_id <= 0:
            return jsonify({
                'message': '无效的用户ID',
                'error_code': 400
            }), 400
        
        # 调用控制器删除用户
        result = user_service.delete_user(user_id)
        
        if result:
            return jsonify({
                'success': True,
                'message': '用户已成功删除'
            }), 200
        else:
            return jsonify({
                'message': '用户不存在',
                'error_code': 404
            }), 404
            
    except Exception as e:
        current_app.logger.error(f'删除用户错误: {str(e)}')
        return jsonify({
            'message': '删除用户失败，请稍后再试',
            'error_code': 500
        }), 500


@user_bp.route('/logout', methods=['POST'])
@token_required  # 需要JWT认证
@swag_from({
    'tags': ['用户管理'],
    'summary': '用户注销登录',
    'description': '使当前登录的JWT令牌失效，用户需重新登录',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'JWT Token(格式: Bearer {token})',
            'example': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        }
    ],
    'responses': {
        200: {
            'description': '注销成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': '已成功注销'}
                }
            }
        },
        401: {
            'description': '未授权',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': '无效的Token'}
                }
            }
        },
        500: {'description': '服务器内部错误'}
    }
})
def logout():
    success, message = user_service.delete_user(user_id)
    if success:
        return jsonify({'message': message}), 200
    elif message == "用户不存在":
        return jsonify({'message': message}), 404
    else:
        return jsonify({'message': message}), 403