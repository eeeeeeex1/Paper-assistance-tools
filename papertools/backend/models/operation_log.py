# 从 config.database 导入 db，注意根据实际包结构调整路径
from datetime import datetime
from config.database import db 

class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(50), nullable=False)  # 如查看、编辑、删除等
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'))  # 可选，如果操作与论文相关

    def __repr__(self):
        return f"Operation('{self.operation_type}', '{self.timestamp}')"