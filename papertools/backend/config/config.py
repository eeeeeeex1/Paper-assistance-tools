import os
from dotenv import load_dotenv  # 若用 .env 文件加载环境变量，需安装 python-dotenv：pip install python-dotenv

# 加载环境变量（如果有 developmentconfig.env 等文件）
load_dotenv(os.path.join(os.path.dirname(__file__), 'developmentconfig.env'))
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 上传文件配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'store', 'papers')
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB 最大文件大小

class Config:
    # Flask 通用配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # 从环境变量取，没有则用默认（生产环境别用默认）
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

    # SQLAlchemy 配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 配置 MySQL 数据库连接，通过环境变量获取信息，方便不同环境切换
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'mysql+pymysql://root:123456@localhost:3306/paper_system'
    )
    # 上面 URI 格式解释：
    # mysql+pymysql：用 pymysql 驱动连接 MySQL；user 是数据库用户名，password 是密码，localhost 是主机，3306 是端口，your_database 是数据库名
    SWAGGER_TEMPLATE  = {
        "swagger": "2.0",
        "info": {
            "title": "API 文档",
            "description": "用户管理 API 文档",
            "version": "1.0.0"
        },
        "basePath": "/",  # 基础路径
        "schemes": [
            "http",
            "https"
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT 格式:Bearer {token}"
            }
        }
    }

    SWAGGER_CONFIG = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,  # 启用 Swagger UI
        "specs_route": "/swagger/"  # Swagger UI 访问路径
    }


# 可扩展不同环境的配置类，比如开发环境
class DevelopmentConfig(Config):
    DEBUG = True  # 开发环境开启调试模式
    QLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/paper_system'
    JWT_SECRET_KEY = 'f50ce100db7f65247ee79cd3fa6f5e830b0298a435e646c6140fe9f33693fe3b'
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRE_HOURS = 24
# 生产环境配置（示例）
class ProductionConfig(Config):
    DEBUG = False
    # 生产环境可以换更安全的数据库配置，比如不同的主机、用户名等
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'PROD_SQLALCHEMY_DATABASE_URI',
        'mysql+pymysql://prod_user:prod_password@prod_host:3306/prod_database'
    )