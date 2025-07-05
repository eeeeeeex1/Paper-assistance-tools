# backend/app/routes/__init__.py
from flask import Blueprint
from .user_controller import user_bp
from .paper_controller import paper_bp  # 导入论文模块蓝图


def register_blueprints(app):
    """
    注册所有路由蓝图到 Flask 应用
    :param app: Flask 应用实例
    """
    app.register_blueprint(user_bp)
    # app.register_blueprint(paper_bp)  # 其他蓝图注册