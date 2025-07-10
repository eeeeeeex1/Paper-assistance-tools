# tests/test_user_service.py
import pytest
from datetime import datetime,timezone
from backend.models import User,Paper
from backend.config.database import db
from backend.services.user_service import UserService
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/paper_checker'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = '123456'
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['JWT_EXPIRE_HOURS'] = 24

    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        yield app

         # 清理数据库
        db.session.remove()
        db.drop_all()


@pytest.fixture
def service(app):
    with app.app_context():
        yield UserService()

def test_create_user(service):
    username = "testuser"
    password = "TestPass123"
    email = "test@example.com"
    
    user, error = service.create_user(username, password, email)
    
    assert user is not None
    assert error is None
    assert user.username == username
    assert service.verify_password(password, user.password_hash)  # 验证时使用 password_hash
    assert user.email == email
    assert isinstance(user.created_at, datetime)
    assert user.created_at.tzinfo == timezone.utc
# 其他测试用例类似，确保验证时使用 password_hash