# 从各个控制器文件中导入对应的蓝图
from service.user_service import UserService

# 定义 __all__，这样当外部用 from controllers import * 时，会导入这些指定的蓝图
__all__ = ["user_bp"]

# 也可以在这里编写一个用于注册所有蓝图的函数（可选，方便在 app.py 中调用）
def register_blueprints(app):
    """
    将 controllers 里的所有蓝图注册到 Flask 应用实例上
    :param app: Flask 应用实例
    """
    app.register_blueprint(user_bp)
    # 如果后续新增了其他蓝图，在这里补充注册逻辑即可