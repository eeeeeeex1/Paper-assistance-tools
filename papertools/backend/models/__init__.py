from .user import User

# 延迟导入 Paper，避免循环依赖
def get_paper_model():
    from .paper import Paper
    return Paper
def get_operation_model():
    from .operation import Operation
    return Operation
# 定义 __all__，这样当外部用 from models import * 时，会导入这些指定的模型类
__all__ = ['User','Paper','Operation']

# 也可以在这里对模型做一些额外处理（可选，简单项目一般用不到）
# 比如给模型类添加一些全局的查询方法等（不过更推荐在服务层做复杂查询）
