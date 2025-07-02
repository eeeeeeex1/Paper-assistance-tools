from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy()

def init_app(app):
    #移除 URI 中的时区参数
    app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://root:123456@localhost/paper_checker'
    '?charset=utf8mb4&sql_mode=STRICT_TRANS_TABLES'
)

    db.init_app(app)