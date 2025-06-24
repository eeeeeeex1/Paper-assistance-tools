from flask import Flask
from models.user import User 
from models.paper import Paper 
from models.operation_log import Operation 
# 从 config 包导入配置类和数据库实例
from config.config import DevelopmentConfig  
from config.database import db  

# 工厂函数创建 Flask 应用
def create_app():
    app = Flask(__name__)
    # 加载配置（开发环境用 DevelopmentConfig）
    app.config.from_object(DevelopmentConfig)  
    # 初始化数据库，将 db 与 app 绑定
    db.init_app(app)  

    # 【可选】注册蓝图、添加路由等，比如：
    # from config.routes import main_bp
    # app.register_blueprint(main_bp)

     # 直接在工厂函数内定义路由
    @app.route('/test_db')
    def test_db():
        try:
            user = User.query.first()
            if user:
                return jsonify({"status": "success", "data": f"User: {user.username}"})
            else:
                new_user = User(username="test", email="test@example.com")
                db.session.add(new_user)
                db.session.commit()
                return jsonify({"status": "success", "message": "Test user created"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    return app

if __name__ == '__main__':
    app = create_app()
    # 激活应用上下文，创建数据库表（如果模型已定义）
    with app.app_context():
        db.create_all()  
    # 启动应用
    app.run(debug=DevelopmentConfig.DEBUG)  