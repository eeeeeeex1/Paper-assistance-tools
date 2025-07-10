# backend/middleware/timezone.py
from flask import g
from sqlalchemy import event

def setup_timezone_middleware(app, db):
    @app.before_request
    def configure_database_timezone():
        """设置数据库连接时区为北京时间（UTC+8）"""
        def set_timezone(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("SET time_zone = '+8:00';")  # 关键：+8:00
            cursor.close()
        
        if not hasattr(g, 'timezone_setup'):
            event.listen(db.engine, "connect", set_timezone)
            g.timezone_setup = True