# config/__init__.py
from .config import Config, DevelopmentConfig, ProductionConfig

# 可选：设置默认导出的配置类（比如开发环境默认用 DevelopmentConfig）
default_config = DevelopmentConfig

# 让外部可通过 from config import Config 直接导入
__all__ = ["Config", "DevelopmentConfig", "ProductionConfig", "default_config"]