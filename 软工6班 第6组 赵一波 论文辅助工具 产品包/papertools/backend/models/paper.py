# models/paper.py
from backend.config.database import db
from datetime import datetime,timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.utils import secure_filename
from io import BytesIO
from config.logging_config import logger
import docx


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
        nullable=True,
        default=datetime.now(timezone.utc)
    )
    file_path = db.Column(
        db.String(255),
        nullable=True
    )
    content = db.Column(
        db.Text,
        nullable=True
    )  # Text类型支持大文本存储


    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title}', author_id={self.author_id}, status='{self.status}')>"

    @staticmethod
    def is_allowed_file(filename):
        """改进版：正确处理中文和特殊字符文件名"""
        allowed_extensions = {'txt', 'pdf', 'docx'}
        
        # 安全检查：确保文件名不为空
        if not filename:
            return False
            
        # 处理带点的中文文件名（如 "报告.测试.docx"）
        if '.' not in filename:
            return False
            
        # 提取最后一个点后的扩展名并转为小写
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in allowed_extensions
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

    @staticmethod
    def extract_content(content_bytes, filename):
        """提取文件内容（支持 .docx）"""
        if filename.endswith('.docx'):
            try:
                logger.info("begin to fix docx")
                # 将二进制数据转换为文档对象
                docx_file = BytesIO(content_bytes)
                doc = docx.Document(docx_file)
                
                # 提取所有段落文本
                content = "\n".join([para.text for para in doc.paragraphs])
                
                return content
            except Exception as e:
                print(f"提取 docx 内容失败111111111111111: {e}")
                return None
        elif filename.endswith('.pdf'):
            # 处理 PDF 提取（需要 PyPDF2 库）
            from PyPDF2 import PdfReader
            pdf_file = BytesIO(content_bytes)
            reader = PdfReader(pdf_file)
            content = ""
            for page in reader.pages:
                content += page.extract_text() or ""
            return content
        elif filename.endswith('.txt'):
            # 已在服务层处理
            return content_bytes.decode('utf-8', errors='ignore')
        return None