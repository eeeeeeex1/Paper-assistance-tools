from flask_restx import Api

# 创建 API 实例（全局）
api = Api(
    title='论文查重系统 API',
    version='1.0',
    description='论文查重系统的后端 API 文档',
)

# 错误处理（可选）
def configure_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return {'message': '资源未找到'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'message': '服务器内部错误'}, 500