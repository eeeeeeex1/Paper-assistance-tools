# backend/controllers/paper_controller.py
from datetime import datetime
from flask import current_app, request,jsonify
from werkzeug.utils import secure_filename  # 新版本正确导入方式
from dao.paper_dao import PaperDao
from backend.models.operation import Operation
from backend.models.paper import Paper
from backend.config.database import db
from config.logging_config import logger
#zyb----------------------------------------------------
from controller.Copyleaks_controller import CopyleaksService
#zyb----------------------------------------------------
import re
import jieba
from collections import Counter
import requests
import math
from bs4 import BeautifulSoup
import requests  # 添加这行
import os
import uuid
import time
import io
import base64  # 需要安装: pip install textract
import random
from urllib.parse import quote, urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from service.typo_detection_service import Typo_Detection
from typing import Tuple, Dict, Union,List
from werkzeug.datastructures import FileStorage
import pdfplumber
from docx import Document
from config.config import BASE_DIR      # 从配置导入项目根路径

from difflib import SequenceMatcher

class PaperService:
    def __init__(self):
        self.paper_dao = PaperDao()
        self.typo_detection_service =Typo_Detection()
        self.api_key = None
        self.last_api_call_time = 0
        self.min_api_interval = 1  # 两次API请求之间至少间隔1秒
        #zyb-------------------------------------------
        self.api_requests = 0  # 记录请求次数
        self.request_window = 60  # 时间窗口（秒）
        self.max_requests_per_window = 50  # 每窗口最大请求数
        self.last_window_reset = time.time()  # 上次重置时间

        self.copyleaks_service = CopyleaksService()
        self.filestore_path = os.path.join(BASE_DIR, "filestore")
        os.makedirs(self.filestore_path, exist_ok=True)  

        #zyb-------------------------------------------

    def set_api_key(self, api_key):
        """设置Semantic Scholar API Key"""
        self.api_key = api_key
        logger.info("已设置Semantic Scholar API Key")
    #zyb---------------------------------------------------------
    def set_copyleaks_api_key(self, api_key,api_email):
        """设置Copyleaks API Key"""
        logger.info('begin set API key')
        self.copyleaks_service.set_api_key(api_key,api_email)
        logger.info("已设置Copyleaks API Key")


    def check_plagiarism_ai(self, file, num_articles, user_id, paper_id,use_copyleaks=True, api_key="df97c454-3284-4674-aebf-77c55d1b60a6",api_email="zhaoyiboeeeeex1@gmail.com", check_ai=True):
        """
        论文查重主方法（支持多API切换）
        :param use_copyleaks: 是否使用Copyleaks API
        :param check_ai: 是否检测AI生成内容
        """
        logger.info(f"begin service check_plagiarism with {'Copyleaks API' if use_copyleaks else 'Semantic Scholar API'}")
        logger.info('begin ai check')

        # 1. 解析文件内容（原有逻辑不变）
        try:
            filename = file.filename
            if not filename:
                return {'code': 400, 'message': '未上传有效文件', 'data': None}
            logger.info('filename right')
            file_ext = filename.split('.')[-1].lower()
            paper_content = self._extract_file_content(file, file_ext)

            if not paper_content:
                return {'code': 400, 'message': '论文内容为空，无法查重', 'data': None}
            logger.info('filecontent right')
            paper_title = filename.rsplit('.', 1)[0]
            logger.info('end file papercontent')
        except Exception as e:
            return {'code': 500, 'message': f'文件解析失败: {str(e)}', 'data': None}

        try:
            # 2. 根据参数选择API
            if use_copyleaks:
                # 使用Copyleaks API
                if not self.copyleaks_service.api_key and not api_key:
                    return {'code': 400, 'message': '未提供Copyleaks API Key', 'data': None}
                if api_key:
                    self.set_copyleaks_api_key(api_key,api_email)

                logger.info(f"Copyleaks查重 - AI检测: {'开启' if check_ai else '关闭'}")
                api_results = self.copyleaks_service.check_plagiarism(
                    text=paper_content,
                    title=paper_title,
                    num_articles=num_articles,
                    is_ai_content=check_ai
                )
                
                # 处理错误
                if 'error' in api_results:
                    return {'code': 500, 'message': api_results['message'], 'data': None}
                
                # 解析结果
                similar_articles = api_results.get('comparison_results', [])
                avg_similarity = api_results.get('comprehensive_similarity', 0)
                ai_detection = api_results.get('ai_detection', {})

                # 记录操作
                Operation.log_operation(
                    user_id=user_id,
                    paper_id=paper_id,
                    operation_type="similaritycheck",
                    file_name=filename,
                    operation_time=datetime.now(),
                    extra_info={
                        "api_provider": "Copyleaks",
                        "ai_detection": check_ai,
                        "ai_confidence": ai_detection.get("confidence", 0)
                    }
                )
                logger.info('end ai check')
                return {
                    'code': 200,
                    'message': f'查重完成（使用Copyleaks API，AI检测: {"开启" if check_ai else "关闭"}）',
                    'data': {
                        'comprehensive_similarity': 0,
                        'paper_title': paper_title,
                        'comparison_results': [],
                        'num_articles': 0,
                        'using_api': use_copyleaks,
                        'api_provider': 'Copyleaks',
                        'keywords': [],  # 新增空的关键词字段
                        'ai_detection': ai_detection
                    }
                }
            
            else:
                # 原有Semantic Scholar逻辑（保持不变）
                # ... 原有代码 ...
                pass  # 此处省略原有逻辑
            
        except Exception as e:
            logger.error(f"查重过程出错：{str(e)}", exc_info=True)
            return {
                'code': 500,
                'message': f'查重过程出错：{str(e)}',
                'data': {
                    'comprehensive_similarity': 0,
                    'paper_title': paper_title,
                    'comparison_results': [],
                    'num_articles': 0,
                    'using_api': use_copyleaks,
                    'api_provider': 'Copyleaks',
                    'keywords': [],  # 新增空的关键词字段
                    'ai_detection': ai_detection
                }
            }

    #zyb---------------------------------------------------------
    def search_semantic_scholar(self, query, num_articles=5):
        """通过Semantic Scholar API搜索论文（增强频率控制）"""
        current_time = time.time()
        # 新增：时间窗口频率控制
        #zyb---------------------------------------------------
        window_elapsed = current_time - self.last_window_reset
        if window_elapsed > self.request_window:
            # 重置计数器
            self.api_requests = 0
            self.last_window_reset = current_time
        
        # 检查是否超过频率限制
        self.api_requests += 1
        if self.api_requests > self.max_requests_per_window:
            logger.warning(f"达到本地请求频率限制（{self.max_requests_per_window}次/分钟），请稍后再试")
            return {"error": "local_rate_limit", "message": "请求过于频繁，请稍后再试"}
        
        # 原有间隔控制逻辑（保留）
        elapsed = current_time - self.last_api_call_time
        if elapsed < self.min_api_interval:
            wait_time = self.min_api_interval - elapsed
            logger.info(f"等待{wait_time:.2f}秒后再请求API")
            time.sleep(wait_time)
        #zyb---------------------------------------------------

        self.last_api_call_time = time.time()
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        
        params = {
            'query': query,
            'limit': num_articles,
            'fields': 'title,authors,abstract,venue,year,citationCount,referenceCount'
        }
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=15)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get('Retry-After', 30))
                    logger.warning(f"收到API频率限制（429），等待{retry_after}秒后重试（尝试 {attempt+1}/{max_retries}）")
                    time.sleep(retry_after)
                    # 重置本地计数器，避免连续触发限制
                    self.api_requests = 0
                    self.last_window_reset = time.time()
                else:
                    logger.error(f"API HTTP错误 {e.response.status_code}: {e.response.text}")
                    raise
            except Exception as e:
                logger.error(f"API请求异常: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # 指数退避
                    logger.info(f"等待{wait_time}秒后重试（尝试 {attempt+1}/{max_retries}）")
                    time.sleep(wait_time)
                else:
                    raise
    
        return {"error": "max_retries_exceeded", "message": "达到最大重试次数"}


    def __del__(self):
        """类销毁时关闭浏览器"""
        if hasattr(self, 'driver'):
            self.driver.quit()
#zyb--------删除---crawl_google_scholar--------------------------
#zyb--------删除---crawl_google_scholar--------------------------

#zyb--------删除---_extract_google_scholar_article--------------------------
#zyb--------删除---_extract_google_scholar_article--------------------------
    ### 辅助函数：主题关键词提取
    def extract_keywords(self, text, top_n=5):
        """优化关键词提取（增强中文支持）"""
        logger.info("begin extract_keywords")
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\uff00-\uffff]', ' ', text)#清理文本
        words = jieba.cut(text)#分词
        #停用词过滤
        stop_words = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', 
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', 
            '自己', '这个', '那个', '然后', '如果', '所以', '但是', '因为', '或者', '而且'
        ])
        filtered_words = [word for word in words if word and word not in stop_words and len(word) > 1]
        #词频统计
        word_counts = Counter(filtered_words)
        logger.info("end extract_keywords")
        return [word for word, _ in word_counts.most_common(top_n) if re.search(r'[\u4e00-\u9fa5]', word)]

    ### 辅助函数：文本预处理
    def preprocess_text(self, text):
        """优化文本预处理（增加对英文的支持）"""
        if not text:
            return []
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        words = jieba.cut(text)
        stop_words = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', 
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', 
            '自己', 'a', 'an', 'the', 'in', 'on', 'at', 'by', 'for', 'to', 'of', 'with', 'is',
            'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having'
        ])
        return [word for word in words if word and word not in stop_words and len(word) > 1]

    ### 核心功能：论文主题提取
    def extract_theme(self, file,user_id,paper_id):
        """论文主题提取（直接接收文件）"""
        try:
            logger.info("begin  find theme")
            if not file or not file.filename:
                return {'code': 400, 'message': '未上传有效文件'}
            
            filename = file.filename
            file_ext = filename.split('.')[-1].lower()
            paper_content = self._extract_file_content(file, file_ext)
            
            if not paper_content:
                return {'code': 400, 'message': '文件内容为空，无法提取主题'}
            
            processed_text = self.preprocess_text(paper_content)
            keywords = self.extract_keywords(paper_content, top_n=5)
            if not keywords:
                return {'code': 400, 'message': '无法提取主题关键词'}
            
            word_counts = Counter(processed_text)
            top_words = word_counts.most_common(20)
            theme_summary = self._generate_theme_summary(paper_content, keywords, top_words)
            
            paper_title = filename.rsplit('.', 1)[0]
            logger.info(f"end  find theme11111111{theme_summary}")
            result = {
                'title': paper_title,
                'keywords': keywords,
                'top_words': top_words,
                'summary': theme_summary,
                'word_frequency': dict(word_counts),
                'filename': filename
            }
            logger.info(f"end  find theme{theme_summary}")
            #主题提取成功后记录操作
            Operation.log_operation(
                user_id=user_id,
                paper_id=paper_id,
                operation_type="textsummary",
                file_name=filename,
                operation_time=datetime.now()
            )
            return {
                'code': 200,
                'message': '主题提取完成',
                'data': result
            }
        except Exception as e:
            current_app.logger.error(f'主题提取错误: {str(e)}')
            return {'code': 500, 'message': f'主题提取失败: {str(e)}'}

    def _extract_file_content(self, file, file_ext):
        """从文件对象中提取内容（支持多种格式）"""
        try:
            file_bytes = file.read()
            if file_ext == 'txt':
                return file_bytes.decode('utf-8', errors='ignore')
            elif file_ext == 'pdf':
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    return ''.join([page.extract_text() or '' for page in pdf.pages])
            elif file_ext == 'docx':
                from docx import Document
                doc = Document(io.BytesIO(file_bytes))
                return '\n'.join([para.text for para in doc.paragraphs])
            elif file_ext == 'doc':
                import textract
                text = textract.process(io.BytesIO(file_bytes), extension='doc')
                return text.decode('utf-8', errors='ignore')
            else:
                current_app.logger.warning(f'不支持的文件格式: {file_ext}')
                return None
        except Exception as e:
            current_app.logger.error(f'文件解析错误: {str(e)}')
            return None

    def _generate_theme_summary(self, text, keywords, top_words, summary_length=500):
        """生成主题摘要"""
        logger.info("begin theme summary")
        #分割文本
        paragraphs = re.split(r'(。|！|\?|\.|!|\?)', text)
        full_paragraphs = []
        for i in range(0, len(paragraphs), 2):
            if i + 1 < len(paragraphs):
                full_paragraphs.append(paragraphs[i] + paragraphs[i+1])
            else:
                full_paragraphs.append(paragraphs[i])
        #段落评分
        paragraph_scores = []
        for para in full_paragraphs:
            score = 0
            for keyword in keywords:
                score += para.count(keyword)
            for word, _ in top_words:
                score += para.count(word)
            paragraph_scores.append((para, score))
        #排序选择
        paragraph_scores.sort(key=lambda x: x[1], reverse=True)
        if not paragraph_scores:
            return "无法生成主题摘要"
        
        selected_paragraphs = []
        current_length = 0
        for para, _ in paragraph_scores:
            para_length = len(para)
            if current_length + para_length <= summary_length:
                selected_paragraphs.append(para)
                current_length += para_length
            else:
                break
        #结果
        summary = ''.join(selected_paragraphs)
        if len(summary) > summary_length:
            summary = summary[:summary_length] + '...'
        logger.error(f"end theme111111111 summary{summary!r}")
        return summary

    ### 论文基础管理功能
    def get_paper(self, paper_id):
        """获取单个论文信息"""
        paper = self.paper_dao.get_paper_by_id(paper_id)
        if not paper:
            return {'code': 404, 'message': '论文不存在'}
        return {'code': 200, 'message': '获取成功', 'data': paper.to_dict()}
    
    def get_user_papers(self, user_id, page=1, per_page=10):
        """获取用户的所有论文"""
        from backend.models.user import User
        user = User.query.get(user_id)
        if not user:
            return {'code': 404, 'message': '用户不存在'}
        papers = self.paper_dao.get_papers_by_author(user_id)
        return {
            'code': 200,
            'message': '获取成功',
            'data': {
                'user_info': {'user_id': user.id, 'username': user.username},
                'papers': [paper.to_dict() for paper in papers]
            }
        }

    def generate_file_path(self, original_filename):
        """生成唯一文件路径"""
        filename = secure_filename(original_filename)
        ext = os.path.splitext(filename)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join("papers", unique_filename)
        full_path = os.path.join(self.upload_folder, unique_filename)
        return file_path, full_path

    def upload_paper(self, title, author_id, file):
        """
        上传论文：保存文件到 filestore，记录路径到数据库
        :param title: 论文标题
        :param author_id: 作者 ID
        :param file: 前端传来的文件对象
        :return: 保存后的 Paper 模型实例
        """
        try:
            logger.info(f"开始上传文件: {file.filename}")
            # 安全处理文件名（避免路径攻击）
            filename = secure_filename(file.filename)  
            # 生成唯一文件名（防止重名）
            unique_filename = f"{uuid.uuid4().hex}_{filename}"  
            # 拼接完整存储路径：backend/filestore/唯一文件名
            file_path = os.path.join(self.filestore_path, unique_filename)  

            # 保存文件到 filestore
            file.save(file_path)  
            logger.info(f"文件已保存至: {file_path}")
            # 在保存文件后添加
            logger.info(f"绝对路径: {os.path.abspath(file_path)}")
            logger.info(f"文件是否存在: {os.path.exists(file_path)}")
            # 创建 Paper 记录（content 设为 None 或根据需求简化）
            new_paper = Paper(
                title=title,
                author_id=author_id,
                file_path=os.path.relpath(file_path, BASE_DIR),  # 存相对路径，方便后续拼接
                content=None  # 不需要内容提取，直接设为 None
            )

            # 调用 DAO 持久化到数据库
            self.paper_dao.create_paper(new_paper)  
            logger.info(f"论文上传成功 - ID: {new_paper.id}")
            return new_paper.id

        except Exception as e:
            # 上传失败时，删除已保存的文件（若存在）
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"上传失败: {str(e)}", exc_info=True)
            raise
    def check_plagiarism(self, file,num_articles,user_id,paper_id, api_key=None):
        """基于Semantic Scholar API的论文查重（增强健壮性）"""
        logger.info("begin service check_plagiarism with Semantic Scholar API")
        
        # 1. 解析上传文件获取内容
        try:
            filename = file.filename
            if not filename:
                return {
                    'code': 400,
                    'message': '未上传有效文件',
                    'data': None
                }
                
            file_ext = filename.split('.')[-1].lower()
            paper_content = self._extract_file_content(file, file_ext)
            
            if not paper_content:
                return {
                    'code': 400,
                    'message': '论文内容为空，无法查重',
                    'data': None
                }
                
            paper_title = filename.rsplit('.', 1)[0]
            
        except Exception as e:
            return {
                'code': 500,
                'message': f'文件解析失败: {str(e)}',
                'data': None
            }
        
        try:
            # 2. 设置API Key
            if api_key:
                self.set_api_key(api_key)
            
            # 3. 提取关键词
            keywords = self.extract_keywords(paper_content)
            if not keywords:
                keywords = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]{2,}', paper_title)[:3]
                if not keywords:
                    return {
                        'code': 400,
                        'message': '无法生成搜索关键词',
                        'data': None
                    }
                    
            search_query = ' '.join(keywords)
            logger.info(f"Semantic Scholar搜索关键词: {search_query}")
            
            # 4. 通过API获取相似文章
            api_results = self.search_semantic_scholar(search_query, num_articles)
            # 增强错误处理
            if not api_results:
                return {
                    'code': 500,
                    'message': 'Semantic Scholar API请求失败',
                    'data': None
                }
                
            if isinstance(api_results, dict) and 'error' in api_results:
                return {
                    'code': 500,
                    'message': f"API错误: {api_results['message']}",
                    'data': None
                }
                
            if not api_results.get('data'):
                # 尝试使用不同的搜索策略（如使用标题）
                title_query = re.sub(r'[^\w\s]', '', paper_title)
                logger.info(f"尝试备用搜索策略: {title_query}")
                api_results = self.search_semantic_scholar(title_query, num_articles)
                
                if not api_results or not api_results.get('data'):
                    return {
                        'code': 400,
                        'message': '未找到相关学术文献，建议调整论文关键词或内容',
                        'data': {
                            'comprehensive_similarity': 0,  # 确保返回基础数据结构
                            'paper_title': paper_title,
                            'comparison_results': [],
                            'keywords': keywords,
                            'num_articles': 0,
                            'using_api': True
                        }
                    }
            
            #lzj5. 计算相似度并提取相似片段（核心修改）
            similar_articles = api_results['data']
            comparison_results = []
        
            for article in similar_articles:
                abstract = article.get('abstract', '')  # 对比文件内容（文献摘要）
                if not abstract:
                    continue  # 跳过没有摘要的文章
                logger.info(f"Before calling _extract_similar_segments, paper_content: {paper_content}")  # 添加日志
                logger.info(f"Before calling _extract_similar_segments, abstract: {abstract}")  # 添加日志
                # 计算相似度（调用原有方法）
                similarity = self._calculate_advanced_similarity(paper_content, abstract)
            
                # 提取相似片段（调用新增方法）
                similar_segments_text1, similar_segments_text2 = self._extract_similar_segments(
                    paper_content, abstract
                )
            
                # 将相似片段加入结果
                comparison_results.append({
                    'article_title': article['title'],
                    'similarity_rate': round(similarity, 2),
                    'url': article.get('url', f"https://www.semanticscholar.org/paper/{article.get('paperId', '')}"),
                    'authors': ', '.join([author['name'] for author in article.get('authors', [])]),
                    # 新增：相似片段（原文件和对比文件）
                    'similar_segments': {
                        'original': similar_segments_text1,  # 原文件（上传论文）的相似部分
                        'comparison': similar_segments_text2  # 对比文件（文献）的相似部分
                    }
                })
            # 6. 计算综合相似度
            avg_similarity = sum(res['similarity_rate'] for res in comparison_results) / max(1, len(comparison_results))
            
            #查重成功后记录操作
            Operation.log_operation(
                user_id=user_id,
                paper_id=paper_id,
                operation_type="similaritycheck",
                file_name=filename,
                operation_time=datetime.now()
            )
            #lzj7. 返回结果（确保数据结构完整性）

        
            return {
            'code': 200,
            'message': '查重完成（使用Semantic Scholar API）',
            'data': {
                'comprehensive_similarity': round(avg_similarity, 2),
                'paper_title': paper_title,
                'comparison_results': comparison_results,  # 包含相似片段的结果列表
                'keywords': keywords,
                'num_articles': len(comparison_results),
                'using_api': True,
                'api_provider': 'Semantic Scholar',
                'ai_detection': {}
                }
                }
            
        except Exception as e:
            logger.error(f"查重过程出错：{str(e)}", exc_info=True)
            return {
                'code': 500,
                'message': f'查重过程出错：{str(e)}',
                'data': {
                    'comprehensive_similarity': 0,
                    'paper_title': paper_title,
                    'comparison_results': [],
                    'keywords': keywords,
                    'num_articles': 0,
                    'using_api': True
                }
            }

    def _calculate_advanced_similarity(self, text1, text2):
        """改进的相似度计算（结合关键词和语义相似度）"""
        if not text1 or not text2:
            return 0.0
        logger.info('begin _calculate_advanced_similarity')
        # 1. 基于关键词的相似度（原逻辑）
        keywords1 = self.extract_keywords(text1, top_n=10)
        keyword_match = sum(1 for kw in keywords1 if kw in text2)
        keyword_similarity = (keyword_match / len(keywords1)) * 0.4 * 100  # 占40%权重
        
        # 2. 基于词频的相似度
        from collections import Counter
        words1 = re.findall(r'\b[\w]+\b', text1.lower())
        words2 = re.findall(r'\b[\w]+\b', text2.lower())
        count1 = Counter(words1)
        count2 = Counter(words2)
        
        # 计算Jaccard相似度
        intersection = sum((count1 & count2).values())
        union = sum((count1 | count2).values())
        jaccard_similarity = (intersection / union) * 0.3 * 100  # 占30%权重
        
        # 3. 语义相似度（使用简单词嵌入，需安装sentence-transformers）
        semantic_similarity = 0.0
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            # 加载轻量级模型
            model = SentenceTransformer('all-MiniLM-L6-v2')
            # 计算文本嵌入
            embedding1 = model.encode(text1)
            embedding2 = model.encode(text2)
            # 余弦相似度
            cosine_sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
            semantic_similarity = cosine_sim * 0.3 * 100  # 占30%权重
        except Exception as e:
            logger.warning(f"语义相似度计算失败，使用基础算法: {str(e)}")
        
        # 综合相似度
        total_similarity = keyword_similarity + jaccard_similarity + semantic_similarity
        return min(total_similarity, 100.0)  # 限制最大值为100


    def delete_paper(self, paper_id):
        """删除论文"""
        success, message = self.paper_dao.delete_paper(paper_id)
        if not success:
            return {'code': 400, 'message': message}
        return {'code': 200, 'message': message}
    
    ### 错字检测功能
    def check_spelling(self, file: FileStorage,user_id,paper_id) -> Tuple[bool, Dict]:
        """优化版论文错字检测主方法"""
        try:
            logger.info("开始论文错字检测服务")

            # 1. 检查文件有效性
            if not file or file.filename == '':
                return False, '未提供有效文件'
            
            # 2. 解析文件内容
            content = file.stream.read().decode('utf-8')
            
            if not content:
                return False, {"error": "文件内容为空或无法解析", "code": 404}
                
            # 3. 执行错字检测（使用专业库）
            typo_results = self.typo_detection_service._detect_typos(content)
            
            # 4. 生成标记文本
            checked_text = self._format_checked_text(content, typo_results)
            
            logger.info(f"finish,find {len(typo_results)} wrong(s)")
            # 改错成功后记录操作
            Operation.log_operation(
                user_id=user_id,
                paper_id=paper_id,
                operation_type="spellcheck",
                file_name=file.filename,
                operation_time=datetime.now()
            )
            # 4. 转换结果格式（关键修改）
            formatted_results = []
            for typo in typo_results:
                formatted_typo = {
                'position': typo['position'],
                'word': typo['wrong_word'],
                'length': typo['length'],
                'suggestions': typo['suggestions'],
                'context': typo['context']
                }
                formatted_results.append(formatted_typo)
        
            return True, {
            "total_typos": len(formatted_results),
            "typo_details": formatted_results,
            "checked_text": checked_text,
            "original_text": content
            }
            
        except FileNotFoundError:
            logger.error("文件no exist")
            return False, {"error": "文件不存在", "code": 404}
        except UnicodeDecodeError:
            logger.error("文件编码错误，无法解析")
            return False, {"error": "文件code wrong，请检查文件格式", "code": 400}
        except Exception as e:
            logger.error(f"错字检测服务fail: {str(e)}", exc_info=True)
            return False, {"error": f"错字检测失败: {str(e)}", "code": 500}
        finally:
            logger.info("spelling end")

    def _format_checked_text(self, content: str, typo_results: List[Dict]) -> str:
        """生成标记错字的文本，适配前端HTML格式"""
        if not typo_results:
            return content
            
        # 按位置倒序排序，避免插入标记后位置偏移
        for result in sorted(typo_results, key=lambda x: x['position'], reverse=True):
            pos = result['position']
            word = result['wrong_word']
            suggestions = result['suggestions']
            
            # 生成后端标记，前端会转换为HTML
            marker = f"[TYPO:{suggestions[0]}]"  # 取第一个建议
            #marker = f'[TYPO:{",".join(suggestions)}]'
            content = f"{content[:pos]}{marker}{word}{marker}{content[pos+len(word):]}"
            
        return content
    

    def _get_context(self, text: str, position: int, length: int) -> str:
        """获取错字上下文"""
        start = max(0, position - length)
        end = min(len(text), position + length)
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        return f"{prefix}{text[start:end]}{suffix}"
    #lmk------------------------------------------------------------
    def get_total_paper_count(self):
        """获取上传的论文总数"""
        try:
            logger.info('Calling DAO layer to get total paper count')
            total_count = self.paper_dao.get_total_paper_count()
            logger.info(f"Total paper count: {total_count}")
            return total_count
        except Exception as e:
            logger.error(f"获取论文总数失败: {str(e)}")
            raise ValueError(f"获取论文总数失败: {str(e)}")
#lmk------------------------------------------------------------

#lzj----------------------------------------------------------------------------

    def _extract_similar_segments(self, text1: str, text2: str) -> tuple:
        """
        提取两段文本中相似的段落（关键词提取优化版）
        :param text1: 原文件文本（上传的论文）
        :param text2: 对比文件文本（相似文献）
        :return: 原文件相似段落列表、对比文件相似段落列表
        """
        logger.info(f"text1 length: {len(text1)}, text2 length: {len(text2)}")
        logger.info('开始检查相似段落（关键词语义匹配模式）')

        # 按段落分割（保留原始换行）
        def split_paragraphs(text):
            paragraphs = re.split(r'(\n+)', text)
            combined = []
            current_para = ""
            for part in paragraphs:
                if re.fullmatch(r'\n+', part):
                    if current_para:
                        combined.append(current_para)
                        current_para = ""
                    combined.append(part)
                else:
                    current_para += part
            if current_para:
                combined.append(current_para)
            return [p for p in combined if p.strip()]

        # 文本预处理（保留中文、字母、数字）
        def preprocess_text(text):
            text = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', text.lower())
            return re.sub(r'\s+', ' ', text).strip()

        # 分割文本
        original_paragraphs1 = split_paragraphs(text1)
        original_paragraphs2 = split_paragraphs(text2)

        # 预处理文本
        processed_paragraphs1 = [preprocess_text(p) for p in original_paragraphs1]
        processed_paragraphs2 = [preprocess_text(p) for p in original_paragraphs2]

        logger.info(f"文本1分割为 {len(original_paragraphs1)} 个段落，文本2分割为 {len(original_paragraphs2)} 个段落")

        # 存储相似段落对
        similar_pairs = []

        # --------------------- 关键词提取模块 ---------------------
        import jieba
        from collections import defaultdict
        import jieba.analyse

        # 加载停用词
        stopwords = set(['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己'])

        # 提取段落关键词（结合TextRank和TF-IDF）
        def extract_keywords(paragraph, top_k=5):
            if not paragraph:
                return []
                
            # 使用jieba的textrank提取关键词
            keywords = jieba.analyse.textrank(paragraph, topK=top_k, withWeight=True, allowPOS=('ns', 'n', 'vn', 'v'))
            
            # 过滤停用词并确保词长>=2
            keywords = [(word, weight) for word, weight in keywords 
                    if word not in stopwords and len(word) >= 2]
            
            return keywords if keywords else []  # 确保至少返回空列表

        # 提取所有段落的关键词
        keywords1 = [extract_keywords(p) for p in processed_paragraphs1]
        keywords2 = [extract_keywords(p) for p in processed_paragraphs2]
        
        # 提取所有关键词的集合（用于句子关键词计数）
        all_keywords = set()
        for para_keywords in keywords1 + keywords2:
            for word, _ in para_keywords:
                all_keywords.add(word)

        # --------------------- 句子级关键词标记 ---------------------
        # 按句子分割并标记关键词最多的句子
        def mark_keyword_sentences(paragraph, keywords_set):
            # 按句子分割（中文句号、问号、感叹号）
            sentences = re.split(r'([。？！])', paragraph)
            combined_sentences = []
            current_sentence = ""
            
            for i, part in enumerate(sentences):
                current_sentence += part
                # 如果是标点符号或者最后一部分，组成一个完整句子
                if i % 2 == 1 or i == len(sentences) - 1:
                    combined_sentences.append(current_sentence)
                    current_sentence = ""
            
            # 计算每个句子的关键词数量
            sentence_keyword_counts = []
            for sentence in combined_sentences:
                count = sum(1 for keyword in keywords_set if keyword in sentence)
                sentence_keyword_counts.append((sentence, count))
            
            # 找到关键词最多的句子
            max_count = max([count for _, count in sentence_keyword_counts], default=0)
            if max_count == 0:
                return paragraph  # 如果没有关键词，直接返回原段落
            
            # 标记关键词最多的句子
            marked_paragraph = ""
            for sentence, count in sentence_keyword_counts:
                if count == max_count:
                    marked_paragraph += f"<mark>{sentence}</mark>"
                else:
                    marked_paragraph += sentence
            
            return marked_paragraph

        # --------------------- 相似度计算模块 ---------------------
        # 计算关键词重叠率
        def keyword_overlap(kw1, kw2):
            set1 = set(word for word, _ in kw1)
            set2 = set(word for word, _ in kw2)
            overlap = set1 & set2
            return len(overlap) / max(len(set1), len(set2)) if max(len(set1), len(set2)) > 0 else 0

        # 改进的字符级相似度计算
        def char_similarity(para1, para2):
            # 忽略短文本
            if len(para1) < 10 or len(para2) < 10:
                return 0
            return SequenceMatcher(None, para1, para2).ratio()

        # 综合相似度计算（提高关键词权重，调整阈值）
        def combined_similarity(kw1, kw2, para1, para2):
            # 关键词重叠率（权重60%）
            kw_sim = keyword_overlap(kw1, kw2)
            # 字符级相似度（权重40%）
            char_sim = char_similarity(para1, para2)
            # 综合相似度（阈值提高到0.35）
            return kw_sim * 0.6 + char_sim * 0.4

        # --------------------- 段落匹配主逻辑 ---------------------
        for i, (para1, kw1) in enumerate(zip(processed_paragraphs1, keywords1)):
            if len(para1.split()) < 5:  # 增加段落长度阈值
                continue
                
            for j, (para2, kw2) in enumerate(zip(processed_paragraphs2, keywords2)):
                if len(para2.split()) < 5:
                    continue
                    
                # 计算综合相似度
                sim = combined_similarity(kw1, kw2, para1, para2)
                if sim >= 0.35:  # 提高相似度阈值
                    # 提取当前段落的关键词集合
                    current_keywords = set(word for word, _ in kw1 + kw2)
                    
                    # 标记关键词最多的句子
                    marked_original1 = mark_keyword_sentences(original_paragraphs1[i], current_keywords)
                    marked_original2 = mark_keyword_sentences(original_paragraphs2[j], current_keywords)
                    
                    similar_pairs.append({
                        'index1': i,
                        'index2': j,
                        'similarity': sim,
                        'original1': original_paragraphs1[i],
                        'original2': original_paragraphs2[j],
                        'marked_original1': marked_original1,
                        'marked_original2': marked_original2
                    })

        # --------------------- 结果去重与排序 ---------------------
        unique_pairs = []
        seen = set()
        for pair in sorted(similar_pairs, key=lambda x: x['similarity'], reverse=True):
            # 改进的去重逻辑：基于段落内容相似度
            key1 = (pair['index1'], pair['index2'])
            key2 = (pair['index2'], pair['index1'])
            
            # 检查是否已存在相似内容
            original1 = pair['original1'].strip()
            original2 = pair['original2'].strip()
            
            # 计算原始文本的相似度
            original_sim = SequenceMatcher(None, original1, original2).ratio()
            
            # 如果两段文本几乎相同，只保留一个
            if original_sim > 0.95:
                continue
                
            if key1 not in seen and key2 not in seen:
                seen.add(key1)
                seen.add(key2)
                unique_pairs.append(pair)
                if len(unique_pairs) >= 100:  # 减少最大保留数量
                    break

        logger.info(f"找到 {len(unique_pairs)} 个相似段落对（关键词语义匹配模式）")

        # 构建输出结果
        segments1 = []
        segments2 = []
        for pair in sorted(unique_pairs, key=lambda x: (x['index1'], x['index2'])):
            segments1.append({
                'content': pair['original1'],
                'marked_content': pair['marked_original1'],
                'similarity': round(pair['similarity'], 2),
                'matched_with': pair['index2']
            })
            segments2.append({
                'content': pair['original2'],
                'marked_content': pair['marked_original2'],
                'similarity': round(pair['similarity'], 2),
                'matched_with': pair['index1']
            })
        logger.info("提取的相似片段 - 文本1: %s, 文本2: %s", segments1, segments2)
        return segments1, segments2
        
    def check_local_plagiarism(self, file1, file2,user_id):
        """本地文件查重"""
        try:
            # 提取文件内容
            logger.info('begin local check')
            file_ext1 = file1.filename.split('.')[-1].lower()
            paper_content1 = self._extract_file_content(file1, file_ext1)
            file_ext2 = file2.filename.split('.')[-1].lower()
            paper_content2 = self._extract_file_content(file2, file_ext2)
            filename=file1.name
            if not paper_content1 or not paper_content2:
                return {
                    'code': 400,
                    'message': '文件内容为空，无法查重',
                    'data': None
                }
            # 计算相似度
            similarity = self._calculate_advanced_similarity(paper_content1, paper_content2)
            similarity = float(similarity)  # 新增这一行s
            # 提取相似片段
            similar_segments_text1, similar_segments_text2 = self._extract_similar_segments(
                paper_content1, paper_content2
            )

            comparison_results = [
                {
                    'article_title': file2.filename,
                    'similarity_rate': round(similarity, 2),
                    'url': '',
                    'authors': '',
                    'similar_segments': {
                        'original': similar_segments_text1,
                        'comparison': similar_segments_text2
                    }
                }
            ]

            # 计算综合相似度
            avg_similarity = sum(res['similarity_rate'] for res in comparison_results) / max(1, len(comparison_results))

            Operation.log_operation(
                user_id=user_id,
                paper_id=None,
                operation_type="similaritycheck",
                file_name=filename,
                operation_time=datetime.now()
            )


            return {
                'code': 200,
                'message': '查重完成（本地文件对比）',
                'data': {
                    'comprehensive_similarity': round(avg_similarity, 2),
                    'paper_title': file1.filename,
                    'comparison_results': comparison_results,
                    'keywords': [],
                    'num_articles': len(comparison_results),
                    'using_api': False,
                    'api_provider': '本地对比',
                    'ai_detection': {}
                }
            }
        except Exception as e:
            logger.error(f"查重过程出错：{str(e)}", exc_info=True)
            return {
                'code': 500,
                'message': f'查重过程出错：{str(e)}',
                'data': {
                    'comprehensive_similarity': 0,
                    'paper_title': file1.filename,
                    'comparison_results': [],
                    'keywords': [],
                    'num_articles': 0,
                    'using_api': False,
                    'api_provider': '本地对比',
                    'ai_detection': {}
                }
            }