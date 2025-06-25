# app.py (添加这两行)
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))  # 添加项目根目录到 sys.path


from flask import Flask
from models.user import User
from flasgger import Swagger
# 从 config 包导入配置类和数据库实例
from config.config import DevelopmentConfig
#from config.database import db
from config.database import db  # 导入 db 实例
from routes.user_route import user_bp  # 导入用户蓝图
from flask_cors import CORS  # 引入 CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from routes.user_route import user_bp


# 工厂函数创建 Flask 应用
def create_app():
    app = Flask(__name__)
    # 加载配置（开发环境用 DevelopmentConfig）
    #app.config.from_object(DevelopmentConfig)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/paper_checker'  # 数据库连接 URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # 初始化数据库，将 db 与 app 绑定
    #db.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)# 初始化迁移工具

    # 导入所有模型（确保 Flask-Migrate 能发现它们）
    from backend.models.user import User

    app.register_blueprint(user_bp, url_prefix='/api/user')

 
    # 配置 CORS（允许前端跨域访问）
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
    
    # 配置 Swagger
    swagger_template = {
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
                "description": "JWT 格式：Bearer {token}"
            }
        }
    }

    swagger_config = {
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

# 初始化 Swagger
    swagger = Swagger(app, template=swagger_template, config=swagger_config)


    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():

        conn = db.engine.connect()
        conn.close()
        # 清除所有表
        #db.reflect()
        #db.drop_all()

        # 确保metadata清理干净
        #db.metadata.clear()

        # 重新创建
        db.create_all()
        print("已执行 db.create_all()")
        
         # 检查表是否创建
    
    app.run(debug=DevelopmentConfig.DEBUG)