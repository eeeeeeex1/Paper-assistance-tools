# app.py (添加这两行)
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))  # 添加项目根目录到 sys.path
from dao.paper_dao import PaperDao
from flask import Flask
from flasgger import Swagger
# 从 config 包导入配置类和数据库实例
from backend.config import DevelopmentConfig
#from config.database import db
from backend.config.database import db  # 导入 db 实例
from flask_cors import CORS  # 引入 CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#-----------------------------------------------------------------
# 工厂函数创建 Flask 应用
def create_app():
    app = Flask(__name__)
    # 加载配置（开发环境用 DevelopmentConfig）
    app.config.from_object(DevelopmentConfig)
    app.config['UPLOAD_FOLDER'] = 'uploads'  # 明确设置上传文件夹
    # 初始化数据库，将 db 与 app 绑定
    #db.init_app(app)
    db.init_app(app)

    migrate = Migrate(app, db)# 初始化迁移工具

    # 导入所有模型（确保 Flask-Migrate 能发现它们）
    from backend.models.user import User
    from backend.models.paper import Paper
    from backend.models.operation import Operation

    # 配置 CORS（允许前端跨域访问）
    CORS(app, origins=["http://localhost:5173"], supports_credentials=False)

    from controller.paper_controller import paper_bp
    from controller.user_controller import user_bp
    from controller.operation_controller import operation_bp 

    # 配置 Swagger
    app.register_blueprint(user_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(operation_bp)


    swagger_template = app.config['SWAGGER_TEMPLATE']
    swagger_config = app.config['SWAGGER_CONFIG']
    # 初始化 Swagger
    swagger = Swagger(app, template=swagger_template, config=swagger_config)
    
    return app
#-------------------------------------------------------

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