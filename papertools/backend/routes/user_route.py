# backend/app/routes/user_route.py
from flask import Blueprint, request, jsonify
from flasgger import swag_from  # 导入 Swagger 装饰器
from controllers.user_controller import UserController
import jwt
from datetime import datetime, timedelta  # 需要添加这行导入

user_bp = Blueprint('user', __name__, url_prefix='/api/user')
user_controller = UserController()

# 示例 1：用户注册（简化版 Swagger 配置）
@user_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['用户管理'],
    'summary': '用户注册',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': '用户名'},
                    'password': {'type': 'string', 'description': '密码'},
                    'email': {'type': 'string', 'description': '邮箱'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': '注册成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'user_id': {'type': 'integer'}
                }
            }
        },
        '400': {'description': '参数错误'}
    }
})
def register():
    data = request.get_json()
    result = user_controller.register(data)
    return jsonify(result)

# 示例 2：用户登录（带认证的接口）

# 测试用登录接口（硬编码验证）
@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        account = data.get('account')
        password = data.get('password')

        # 硬编码验证（仅用于测试！）
        if account == 'admin' and password == '123456':
            # 生成 JWT Token（实际应使用安全密钥）
            payload = {
                'user_id': 1,
                'account': 'admin',
                'role': 'admin',
                'exp': datetime.utcnow() + timedelta(hours=1)
            }
            token = jwt.encode(payload, 'test-secret-key', algorithm='HS256')
            
            return jsonify({
                'success': True,
                'message': '登录成功',
                'token': token,
                'user_info': {
                    'id': 1,
                    'account': 'admin',
                    'name': '管理员',
                    'role': 'admin'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '账号或密码错误'
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500
# 示例 3：获取用户信息（需要 Token 认证）
@user_bp.route('/info', methods=['GET'])
@swag_from({
    'tags': ['用户管理'],
    'summary': '获取用户信息',
    'security': [{'Bearer': []}],  # 声明需要 Token 认证
    'responses': {
        '200': {
            'description': '用户信息',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'username': {'type': 'string'},
                    'email': {'type': 'string'}
                }
            }
        },
        '401': {'description': '未授权'}
    }
})
def get_user_info():
    token = request.headers.get('Authorization')
    result = user_controller.get_user_info(token)
    return jsonify(result)