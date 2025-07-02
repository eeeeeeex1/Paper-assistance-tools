from flask import current_app
from backend.models.user import  User
from backend.models.paper import Paper # 导入相关模型
from backend.config.database import db  # 导入数据库实例
import os
import logging
from datetime import datetime
import uuid
import subprocess
import json
import jieba
import math
import aiohttp
from bs4 import BeautifulSoup
import requests
from difflib import SequenceMatcher
import re
from collections import Counter
import asyncio
from werkzeug.utils import secure_filename

# 初始化日志记录器
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class PaperDao:

    def init_upload_folder(self, app):
        # 从 app 中获取配置，而非 current_app
        self.upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        self.allowed_extensions = {'pdf', 'docx','doc', 'txt'}  # 允许的文件类型
        self.logger.info(f"上传文件夹已初始化为: {self.upload_folder}")

    def allowed_file(self, filename):
        """检查文件扩展名是否允许"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def generate_unique_filename(self, original_filename):
        """生成唯一文件名，避免冲突"""
        try:
            # 确保文件名是字符串
            if isinstance(original_filename, bytes):
                original_filename = original_filename.decode('utf-8', errors='replace')
            
            ext = os.path.splitext(original_filename)[1]
            unique_id = uuid.uuid4().hex
            return f"{unique_id}{ext}"
        except Exception as e:
            self.logger.error(f"生成唯一文件名失败: {str(e)}")
            return f"{uuid.uuid4().hex}.unknown"
    
    def get_paper_by_id(self, paper_id):
        """通过ID获取论文"""
        return Paper.query.get(paper_id)
    
    def get_papers_by_author(self, author_id):
        """通过作者ID获取该作者的所有论文"""
        return Paper.query.filter_by(author_id=author_id).all()
    
    def get_all_papers(self, page=1, per_page=10):
        """获取所有论文（支持分页）"""
        return Paper.query.paginate(page=page, per_page=per_page, error_out=False)
    
    def upload_paper(self, title, author_id, file):
        self.logger.info(f"开始上传论文: {title}, 作者ID: {author_id}")
        logger.info(f"begin dao upload paper")
        """上传论文（改进版）"""
         # 确保上传文件夹已初始化
        if not self.upload_folder:
            self.logger.error("上传文件夹未初始化")
            return None, "系统配置错误，请联系管理员"
        
        # 检查作者是否存在
        author = User.query.get(author_id)
        if not author:
            self.logger.warning(f"作者不存在: {author_id}")
            return None, "作者不存在"
        
        # 检查文件是否存在且合法
        if file is None or file.filename == '':
            self.logger.warning("未选择文件")
            return None, "未选择文件"
            
        if not self.allowed_file(file.filename):
            self.logger.warning(f"不支持的文件类型: {file.filename}")
            return None, f"不支持的文件类型，允许的类型: {', '.join(self.allowed_extensions)}"
        
        # 生成唯一文件名并保存文件
        unique_filename = self.generate_unique_filename(file.filename)
        save_path = os.path.join(self.upload_folder, unique_filename)
        
        self.logger.info(f"准备保存文件: {save_path}")
        
        try:
            # 确保上传目录存在
            os.makedirs(self.upload_folder, exist_ok=True)
            
            # 保存文件
            file.save(save_path)
            self.logger.info(f"文件已保存: {save_path}")
            
            # 提取文件内容
            content = self._extract_content(save_path)
            self.logger.info(f"成功提取文件内容，长度: {len(content)}")
            
            # 创建论文对象
            new_paper = Paper(
                title=title,
                author_id=author_id,
                upload_time=datetime.utcnow(),
                file_path=unique_filename,  # 只保存文件名，而非完整路径
                content=content
            )
            
            # 保存到数据库
            self.db.session.add(new_paper)
            self.db.session.commit()
            self.logger.info(f"论文已成功保存到数据库,ID: {new_paper.id}")
            logger.info(f"end dao upload paper")
            return new_paper, None
            
        except Exception as e:
            # 记录详细的错误信息
            self.logger.error(f"上传失败: {str(e)}", exc_info=True)
            
            # 出错时回滚事务并删除已上传的文件
            self.db.session.rollback()
            if os.path.exists(save_path):
                os.remove(save_path)
                self.logger.info(f"已删除临时文件: {save_path}")
                
            return None, f"上传失败: {str(e)}"
    
    def delete_paper(self, paper_id):
        """删除论文"""
        try:
            # 检查论文是否存在
            paper = Paper.query.get(paper_id)
            if not paper:
                return False, "论文不存在"
            
            # 删除文件（如果存在）
            if paper.file_path and os.path.exists(paper.file_path):
                os.remove(paper.file_path)
            
            db.session.delete(paper)
            db.session.commit()
            return True, "删除成功"
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除论文失败: {str(e)}")
            return False, f"删除论文失败: {str(e)}"
    
    def check_spelling(self, paper_id):
        """论文错字检测"""
        paper = self.get_paper_by_id(paper_id)
        if not paper:
            return False, "论文不存在"
        
        try:
            # 假设文件是文本格式，实际应用中可能需要根据文件类型处理
            if not os.path.exists(paper.file_path):
                return False, "论文文件不存在"
            
            # 这里使用简单示例，实际应集成专业拼写检查工具
            with open(paper.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 模拟拼写检查（实际应替换为真实检查逻辑）
            # 这里仅返回错误数量和示例
            error_count = len([word for word in content.split() if len(word) < 3 or 'x' in word])
            result = {
                "error_count": error_count,
                "sample_errors": ["示例错误1", "示例错误2"] if error_count > 0 else [],
                "suggestions": ["建议1", "建议2"] if error_count > 0 else []
            }
            
            return True, result
        except Exception as e:
            logger.error(f"拼写检查失败: {str(e)}")
            return False, f"拼写检查失败: {str(e)}"
    

#论文查重关键函数
    def check_plagiarism(self, paper_id, compare_with=None):
        """论文查重"""
        paper = self.get_paper_by_id(paper_id)
        if not paper:
            return False, "论文不存在"
        
        try:
            if not os.path.exists(paper.file_path):
                return False, "论文文件不存在"
            
            with open(paper.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 模拟查重逻辑（实际应集成专业查重引擎）
            # 这里假设与系统中其他论文进行比较
            similar_papers = []
            if compare_with:
                # 与指定论文比较
                compare_paper = self.get_paper_by_id(compare_with)
                if compare_paper and os.path.exists(compare_paper.file_path):
                    with open(compare_paper.file_path, 'r', encoding='utf-8') as f:
                        compare_content = f.read()
                    similarity = SequenceMatcher(None, content, compare_content).ratio()
                    similar_papers.append({
                        "paper_id": compare_paper.id,
                        "title": compare_paper.title,
                        "similarity": similarity
                    })
            else:
                # 与所有其他论文比较（简化示例）
                all_papers = Paper.query.filter(Paper.id != paper_id).all()
                for p in all_papers:
                    if os.path.exists(p.file_path):
                        with open(p.file_path, 'r', encoding='utf-8') as f:
                            compare_content = f.read()
                        similarity = SequenceMatcher(None, content, compare_content).ratio()
                        if similarity > 0.2:  # 设定相似度阈值
                            similar_papers.append({
                                "paper_id": p.id,
                                "title": p.title,
                                "similarity": similarity
                            })
            
            # 计算总体重复率（简化示例）
            total_similarity = sum(p["similarity"] for p in similar_papers) / max(1, len(similar_papers))
            
            result = {
                "total_similarity": total_similarity,
                "similar_papers": similar_papers,
                "plagiarism_report": f"论文重复率为 {total_similarity*100:.2f}%"
            }
            
            return True, result
        except Exception as e:
            logger.error(f"查重失败: {str(e)}")
            return False, f"查重失败: {str(e)}"
        #
        

    
    def extract_theme(self, paper_id):
        """论文主题提取"""
        paper = self.get_paper_by_id(paper_id)
        if not paper:
            return False, "论文不存在"
        
        try:
            if not os.path.exists(paper.file_path):
                return False, "论文文件不存在"
            
            with open(paper.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 模拟主题提取（实际应使用NLP库如spaCy、TextRank等）
            # 这里仅提取高频词作为主题
            words = content.split()
            word_freq = {}
            for word in words:
                if len(word) > 2:  # 忽略短词
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # 获取前5个高频词作为主题
            themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            theme_names = [word for word, freq in themes]
            
            result = {
                "themes": theme_names,
                "theme_keywords": themes,
                "theme_analysis": f"论文主题围绕 {', '.join(theme_names)}"
            }
            
            return True, result
        except Exception as e:
            logger.error(f"主题提取失败: {str(e)}")
            return False, f"主题提取失败: {str(e)}"
            
    def create_paper(self, paper: Paper) -> Paper:
        """创建新论文记录"""
        try:
            logger.info("begin dao")
            # 添加到会话
            db.session.add(paper)
            
            # 提交事务
            db.session.commit()
            logger.info("end dao")
            # 返回带 ID 的实例
            return paper
            
        except Exception as e:
            # 回滚事务
            db.session.rollback()
            raise e  # 抛回异常由上层处理
#--------------------------------------------------
    def get_total_paper_count(self):
        """获取上传的论文总数"""
        return Paper.query.count()