import unittest
from app import create_app  # 导入你的 Flask 应用工厂函数
from models.user import User  # 导入数据库和用户模型
from config.database import db  # 导入数据库配置
import json
from datetime import datetime

class TestUserRegistration(unittest.TestCase):
    def setUp(self):
        """在每个测试前设置测试环境"""
        # 创建测试应用实例
        self.app = create_app()  # 使用测试配置
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建测试数据库
        db.create_all()
        
        # 创建测试客户端
        self.client = self.app.test_client()
        
        # 确保数据库为空
        User.query.delete()
        db.session.commit()

    def tearDown(self):
        """在每个测试后清理测试环境"""
        # 清除数据库
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_successful_registration(self):
        """测试成功注册场景"""
        # 准备测试数据
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!',
            'email': 'test@example.com'
        }
        
        # 发送注册请求
        response = self.client.post(
            '/api/users/register',  # 替换为实际的注册路由
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # 解析响应
        response_data = json.loads(response.data)
        
        # 验证响应状态码和消息
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['code'], 201)
        self.assertEqual(response_data['message'], '注册成功')
        
        # 验证数据库中是否有该用户
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        
        # 验证密码是否已加密存储
        self.assertNotEqual(user.password_hash, 'TestPassword123!')
        
        # 验证创建时间和更新时间是否正确设置
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        self.assertEqual(user.created_at, user.updated_at)

    def test_duplicate_username(self):
        """测试重复用户名注册"""
        # 先创建一个用户
        user = User(username='existing', password_hash='hashed', email='existing@example.com')
        db.session.add(user)
        db.session.commit()
        
        # 尝试使用相同用户名注册
        data = {
            'username': 'existing',
            'password': 'NewPassword123!',
            'email': 'new@example.com'
        }
        
        response = self.client.post(
            '/api/users/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        response_data = json.loads(response.data)
        
        # 验证响应状态码和错误消息
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['code'], 400)
        self.assertIn('用户名已存在', response_data['message'])

    def test_duplicate_email(self):
        """测试重复邮箱注册"""
        # 先创建一个用户
        user = User(username='existing', password_hash='hashed', email='existing@example.com')
        db.session.add(user)
        db.session.commit()
        
        # 尝试使用相同邮箱注册
        data = {
            'username': 'newuser',
            'password': 'NewPassword123!',
            'email': 'existing@example.com'
        }
        
        response = self.client.post(
            '/api/users/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        response_data = json.loads(response.data)
        
        # 验证响应状态码和错误消息
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['code'], 400)
        self.assertIn('邮箱已存在', response_data['message'])

    def test_missing_fields(self):
        """测试缺少必填字段的情况"""
        # 缺少邮箱字段
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        
        response = self.client.post(
            '/api/users/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        response_data = json.loads(response.data)
        
        # 验证响应状态码和错误消息
        self.assertEqual(response.status_code, 400)
        self.assertIn('邮箱不能为空', response_data['message'])

    def test_invalid_email_format(self):
        """测试无效邮箱格式"""
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!',
            'email': 'invalid_email'
        }
        
        response = self.client.post(
            '/api/users/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        response_data = json.loads(response.data)
        
        # 验证响应状态码和错误消息
        self.assertEqual(response.status_code, 400)
        self.assertIn('邮箱格式不正确', response_data['message'])

    def test_short_password(self):
        """测试密码长度不足"""
        data = {
            'username': 'testuser',
            'password': 'Short',  # 密码过短
            'email': 'test@example.com'
        }
        
        response = self.client.post(
            '/api/users/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        response_data = json.loads(response.data)
        
        # 验证响应状态码和错误消息
        self.assertEqual(response.status_code, 400)
        self.assertIn('密码长度至少为8个字符', response_data['message'])

if __name__ == '__main__':
    unittest.main()    