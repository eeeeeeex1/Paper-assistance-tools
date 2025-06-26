# backend/models/operation.py
from backend.config.database import db
from datetime import datetime
# models/user_operation.py
from sqlalchemy import BigInteger  # 导入 BigInteger

class Operation(db.Model):
    __tablename__ = 'operations'
    __table_args__ = {'extend_existing': True}  # 支持表结构扩展
    
    id = db.Column(
        db.BigInteger,
        primary_key=True
    )
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey('users.id'),
        nullable=False
    )
    paper_id = db.Column(
        db.BigInteger,
        db.ForeignKey('papers.id', ondelete='CASACDE'), 
        nullable=True
    )
    operation_type = db.Column(
        db.String(50),
        nullable=False
    )
    operation_time = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    
    # 关系映射
    user = db.relationship('User', backref='operations')
    paper = db.relationship('Paper', backref='operations')
    
    def to_dict(self):
        """将操作记录转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'paper_id': self.paper_id,
            'operation_type': self.operation_type,
            'operation_time': self.operation_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_info': self.user.to_dict(include_sensitive=False) if self.user else None,
            'paper_title': self.paper.title if self.paper else None
        }
    
    @staticmethod
    def log_operation(user_id, paper_id, operation_type):
        """记录操作日志（静态方法）"""
        new_operation = Operation(
            user_id=user_id,
            paper_id=paper_id,
            operation_type=operation_type
        )
        db.session.add(new_operation)
        db.session.commit()
        return new_operation