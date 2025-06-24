from datetime import datetime
# 从 config.database 导入 db，注意根据实际包结构调整路径
from config.database import db 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='user')  # user or admin
    papers = db.relationship('Paper', backref='author', lazy=True)
    operations = db.relationship('Operation', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"