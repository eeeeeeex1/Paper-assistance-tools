# 从 config.database 导入 db，注意根据实际包结构调整路径
from datetime import datetime
from config.database import db 

class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    operations = db.relationship('Operation', backref='paper', lazy=True)
    theme = db.Column(db.String(100))  # 提取的论文主题
    similarity_score = db.Column(db.Float)  # 与其他论文的相似度

    def __repr__(self):
        return f"Paper('{self.title}', '{self.upload_date}')"