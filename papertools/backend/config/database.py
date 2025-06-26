from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy()

def init_app(app):
    """
    初始化数据库，将 SQLAlchemy 实例和 Flask 应用关联
    :param app: Flask 应用实例
    """
    db.init_app(app)