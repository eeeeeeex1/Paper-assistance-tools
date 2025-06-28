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

# 初始化日志记录器
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class PaperDao:
    def get_paper_by_id(self, paper_id):
        """通过ID获取论文"""
        return Paper.query.get(paper_id)
    
    def get_papers_by_author(self, author_id):
        """通过作者ID获取该作者的所有论文"""
        return Paper.query.filter_by(author_id=author_id).all()
    
    def get_all_papers(self, page=1, per_page=10):
        """获取所有论文（支持分页）"""
        return Paper.query.paginate(page=page, per_page=per_page, error_out=False)
    
    def upload_paper(self, title, author_id, file_path):
        """上传论文"""
        # 检查作者是否存在
        author = User.query.get(author_id)
        if not author:
            return None, "作者不存在"
        content = self._extract_content(file_path)
        # 创建论文对象
        new_paper = Paper(
            title=title,
            author_id=author_id,
            upload_time=datetime.utcnow(),
            file_path=file_path,
            content=content  # 保存提取的内容
        )
        
        # 保存到数据库
        db.session.add(new_paper)
        db.session.commit()
        
        return new_paper, None
    
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
            
