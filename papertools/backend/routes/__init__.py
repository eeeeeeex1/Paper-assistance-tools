# backend/app/routes/__init__.py
from flask import Blueprint
from .user_route import user_bp  # 导入用户模块蓝图

# 如果有其他路由蓝图，继续导入
# from .paper_routes import paper_bp  

def register_blueprints(app):
    """
    注册所有路由蓝图到 Flask 应用
    :param app: Flask 应用实例
    """
    app.register_blueprint(user_bp)
    # app.register_blueprint(paper_bp)  # 其他蓝图注册