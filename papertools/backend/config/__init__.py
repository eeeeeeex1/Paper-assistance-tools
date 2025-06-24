from flask import Flask
from .config import DevelopmentConfig  # 导入开发环境配置类，生产环境换 ProductionConfig
from .database import db

# 创建 Flask 应用函数（工厂模式常用写法，方便扩展）
def create_app():
    app = Flask(__name__)
    # 加载配置，这里用开发环境配置，实际可根据环境变量切换
    app.config.from_object(DevelopmentConfig)
    
    # 初始化数据库
    db.init_app(app)
    
    # 可以在这里注册蓝图等，比如：
    # from .routes import main_bp
    # app.register_blueprint(main_bp)
    
    return app