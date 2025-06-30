# models/paper.py
from backend.config.database import db
from datetime import datetime,timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.utils import secure_filename

class Paper(db.Model):
    __tablename__ = 'papers'
    __table_args__ = {'extend_existing': True}  # 关键修改

    id = db.Column(
        db.BigInteger,
        primary_key=True
    )
    title = db.Column(
        db.String(255),
        nullable=False
    )
    author_id = db.Column(
        db.Integer,
        nullable=False
    )
    upload_time = db.Column(
        db.DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
    file_path = db.Column(db.String(255))
    content = db.Column(
        db.Text
    )  # Text类型支持大文本存储


    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title}', author_id={self.author_id}, status='{self.status}')>"
    
    # 类方法：验证文件类型
    @classmethod
    def is_allowed_file(cls, filename):
        allowed_extensions = {'pdf', 'docx', 'txt', 'md'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    # 实例方法：获取文件URL
    def get_file_url(self):
        if not self.file_path:
            return None
        # 假设使用Flask的send_from_directory，实际实现需根据应用调整
        return f"/download/{self.id}"
    
    # 实例方法：转换为字典（用于JSON序列化）
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author_id': self.author_id,
            'upload_time': self.upload_time.isoformat(),
            'file_path': self.file_path,
            'file_url': self.get_file_url()
        }