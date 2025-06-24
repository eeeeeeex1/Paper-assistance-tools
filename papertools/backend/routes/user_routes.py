from flask import Blueprint, request, jsonify
from services.user_service import UserService

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    success, message = UserService.register_user(username, password, email)
    if success:
        return jsonify({'message': message}), 201
    else:
        return jsonify({'message': message}), 400

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    success, message, user = UserService.login_user(username, password)
    if success:
        return jsonify({'message': message, 'user_id': user.id}), 200
    else:
        return jsonify({'message': message}), 401

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    success, user = UserService.get_user_info(user_id)
    if success:
        return jsonify({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'registration_date': user.registration_date
        }), 200
    else:
        return jsonify({'message': '用户不存在'}), 404