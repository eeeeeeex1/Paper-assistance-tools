# backend/controllers/paper_controller.py
from flask import current_app, request,jsonify
from werkzeug.utils import secure_filename  # 新版本正确导入方式
from dao.paper_dao import PaperDao
from backend.models.operation import Operation
from backend.models.paper import Paper
from backend.config.database import db
from config.logging_config import logger
from service.ChineseTypoDetector import ChineseTypoDetector
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
from typing import List, Dict, Tuple, Optional
from werkzeug.datastructures import FileStorage
from backend.models.operation import Operation


class PaperService:
    def __init__(self):
        self.paper_dao = PaperDao()
        # 复用浏览器实例（关键优化）
        self.api_key = None
        self.last_api_call_time = 0
        self.min_api_interval = 1  # 两次API请求之间至少间隔1秒
        self.typo_detector = ChineseTypoDetector()  # 假设该类已正确实现
    #---------------------------------------------------------------------------
    def set_api_key(self, api_key):
        """设置Semantic Scholar API Key"""
        self.api_key = api_key
    
    def search_semantic_scholar(self, query, num_articles=5):
        """通过Semantic Scholar API搜索论文（增强频率控制）"""
        # 实现请求间隔控制
        current_time = time.time()
        elapsed = current_time - self.last_api_call_time
        
        if elapsed < self.min_api_interval:
            wait_time = self.min_api_interval - elapsed
            logger.info(f"等待{wait_time:.2f}秒后再请求API")
            time.sleep(wait_time)
        
        self.last_api_call_time = time.time()
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        
        params = {
            'query': query,
            'limit': num_articles,
            'fields': 'title,authors,abstract,venue,year,citationCount,referenceCount'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()  # 检查HTTP状态码
            
            data = response.json()
            if not data.get('data'):
                logger.warning(f"API返回空结果: {data}")
                return None
                
            return data
            
        except requests.exceptions.HTTPError as e:
            # 处理HTTP错误（如401、429等）
            logger.error(f"API HTTP错误 {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 429:  # 限流错误
                return {"error": "rate_limit_exceeded", "message": "请求频率过高，请稍后再试"}
            return None
            
        except requests.exceptions.RequestException as e:
            # 处理网络连接错误
            logger.error(f"API连接错误: {str(e)}")
            return None
            
        except Exception as e:
            # 处理其他意外错误
            logger.error(f"API请求异常: {str(e)}", exc_info=True)
            return None

    def __del__(self):
        """类销毁时关闭浏览器"""
        if hasattr(self, 'driver'):
            self.driver.quit()
### 辅助函数：主题关键词提取
    def extract_keywords(self, text, top_n=5):
        """优化关键词提取（增强中文支持）"""
        logger.info("begin extract_keywords")
        # 去除标点符号和特殊字符（保留中文标点）
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\uff00-\uffff]', ' ', text)
        # 分词
        words = jieba.cut(text)
        # 过滤停用词（扩展中文停用词）
        stop_words = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', 
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', 
            '自己', '这个', '那个', '然后', '如果', '所以', '但是', '因为', '或者', '而且'
        ])
        filtered_words = [word for word in words if word and word not in stop_words and len(word) > 1]
        # 统计词频并取前n个
        word_counts = Counter(filtered_words)
        logger.info("end extract_keywords")
        
        # 确保关键词为中文（维普网主要收录中文文献）
        return [word for word, _ in word_counts.most_common(top_n) if re.search(r'[\u4e00-\u9fa5]', word)]
    def crawl_google_scholar(self, query, num_articles=5):
        """爬取Google Scholar相关论文"""
        articles = []
        try:
            # 编码查询关键词
            encoded_query = quote(query)
            url = f'https://scholar.google.com/scholar?q={encoded_query}&hl=zh-CN&as_sdt=0,5'
            logger.info(f"爬取Google Scholar URL: {url}")
            
            # 使用复用的浏览器实例
            self.driver.get(url)
            
            # 等待搜索结果加载
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gs_ri'))
            )
            
            # 滚动页面加载更多结果
            for _ in range(2):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))
            
            # 解析搜索结果
            results = self.driver.find_elements(By.CSS_SELECTOR, 'div.gs_ri')
            logger.info(f"找到 {len(results)} 条Google Scholar结果")
            
            # 提取前num_articles篇文章
            for result in results[:num_articles]:
                article = self._extract_google_scholar_article(result)
                if article:
                    articles.append(article)
                    # 随机延迟避免反爬
                    time.sleep(random.uniform(3, 6))
            
            return articles
            
        except Exception as e:
            logger.error(f"Google Scholar爬取出错: {str(e)}", exc_info=True)
            return articles

    def _extract_google_scholar_article(self, element):
        """从Google Scholar结果元素中提取论文信息"""
        try:
            # 提取标题和链接
            title_elem = element.find_element(By.CSS_SELECTOR, 'h3 a')
            title = title_elem.text
            url = title_elem.get_attribute('href')
            
            # 提取作者信息
            author_elem = element.find_element(By.CSS_SELECTOR, 'div.gs_a')
            author_text = author_elem.text
            
            # 提取摘要
            abstract_elem = element.find_element(By.CSS_SELECTOR, 'div.gs_rs')
            abstract = abstract_elem.text if abstract_elem else "无摘要"
            
            return {
                'title': title,
                'url': url,
                'authors': author_text,
                'abstract': abstract
            }
            
        except Exception as e:
            logger.warning(f"解析Google Scholar文章出错: {str(e)}")
            return None
#--------------------------------------------------------------------------

    
    def get_paper(self, paper_id):
        """获取单个论文信息"""
        paper = self.paper_dao.get_paper_by_id(paper_id)
        
        if not paper:
            return {
                'code': 404,
                'message': '论文不存在'
            }
        
        return {
            'code': 200,
            'message': '获取成功',
            'data': paper.to_dict()
        }
    
    def get_user_papers(self, user_id, page=1, per_page=10):
        """获取用户的所有论文"""
        # 检查用户是否存在
        from backend.models.user import User
        user = User.query.get(user_id)
        if not user:
            return {
                'code': 404,
                'message': '用户不存在'
            }
        
        papers = self.paper_dao.get_papers_by_author(user_id)
        
        return {
            'code': 200,
            'message': '获取成功',
            'data': {
                'user_info': {
                    'user_id': user.id,
                    'username': user.username
                },
                'papers': [paper.to_dict() for paper in papers]
            }
        }

    def generate_file_path(self, original_filename):
        """生成简单的唯一文件路径（无日期）"""
        # 确保文件名安全
        filename = secure_filename(original_filename)
        ext = os.path.splitext(filename)[1].lower()
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join("papers", unique_filename)  # 存储相对路径
        full_path = os.path.join(self.upload_folder, unique_filename)  # 完整物理路径

        return file_path, full_path
    def upload_paper(self, title, author_id, file):
        """上传逻辑（不保存文件，仅提取内容）"""
        try:
            logger.info(f"开始上传文件: {file.filename}")
            
            # 安全检查文件名
            filename = secure_filename(file.filename)
            #if not Paper.is_allowed_file(filename):
            #    raise ValueError("11111111111111111不支持的文件类型")
                
            # 不保存文件，file_path 设为 None
            file_path = None
            # 尝试提取内容（如果文件类型支持）
            content = None
            if filename.endswith(('.txt', '.pdf', '.docx')):
                # 读取文件内容但不保存
                content_bytes = file.stream.read()
                file.stream.seek(0)  # 重置文件指针
                
                # 将字节转换为字符串（假设文本文件为 UTF-8 编码）
                if filename.endswith('.txt'):
                    try:
                        content = content_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        # 尝试其他编码
                        content = content_bytes.decode('gbk', errors='ignore')
                else:
                    # 对于 PDF/DOCX，使用提取器（需要安装相应库）
                    content = Paper.extract_content(content_bytes, filename)

            logger.info("win")
            # 创建论文记录
            new_paper = Paper(
                title=title,
                author_id=author_id,
                file_path=file_path,  # None
                content=content
            )
            
            #保存到数据库
            self.paper_dao.create_paper(new_paper)
            logger.info(f"论文上传成功 - ID: {new_paper.id}")
            return new_paper
            
        except Exception as e:
            logger.error(f"上传失败: {str(e)}")
            raise


    def delete_paper(self, paper_id):
        """删除论文"""
        success, message = self.paper_dao.delete_paper(paper_id)

        #计入操作记录
        Operation.log_operation(
            user_id=self.paper.author_id,
            paper_id=paper_id,
            operation_type="删除论文",
            file_name="self.paper.title"
        )
        if not success:
            return {
                'code': 400,
                'message': message
            }
        
        return {
            'code': 200,
            'message': message
        }
    
    def check_spelling(self, file: FileStorage) -> Tuple[bool, Dict[str, any]]:
        """论文错字检测主方法（增强错误处理与类型提示）"""
        try:
            logger.info("开始论文错字检测服务")
            
            # 1. 文件有效性检查（增强类型判断）
            if not isinstance(file, FileStorage) or not file.filename:
                return False, {"error": "未提供有效文件", "code": 400}
                
            # 2. 解析文件内容（添加返回值类型检查）
            file_ext = file.filename.split('.')[-1].lower()
            content: Optional[str] = self._extract_file_content(file, file_ext)
            
            if not content:
                return False, {"error": "文件内容为空或无法解析", "code": 404}
                
            # 3. 执行错字检测（明确返回值类型）
            typo_results: List[Dict[str, any]] = self.typo_detector.detect_typos(content)
            
            # 4. 生成标记文本（添加空结果处理）
            checked_text: str = self.typo_detector.highlight_typos(content, typo_results)
            
            logger.info(f"错字检测完成，发现 {len(typo_results)} 处错误")
            return True, {
                "status": "success",
                "total_typos": len(typo_results),
                "typo_details": typo_results,
                "checked_text": checked_text,
                "content_length": len(content)
            }
            
        except FileNotFoundError:
            logger.error("文件不存在")
            return False, {"error": "文件不存在", "code": 404}
        except UnicodeDecodeError:
            logger.error("文件编码错误，无法解析")
            return False, {"error": "文件编码错误，请检查文件格式", "code": 400}
        except Exception as e:
            logger.error(f"错字检测服务异常: {str(e)}", exc_info=True)
            return False, {"error": f"错字检测失败: {str(e)}", "code": 500}
        finally:
            logger.info("论文错字检测服务结束")

    def check_plagiarism(self, file,userid,num_articles=5, api_key=None):
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
            
            # 5. 计算相似度
            similar_articles = api_results['data']
            comparison_results = []
            
            for article in similar_articles:
                abstract = article.get('abstract', '')
                if not abstract:
                    continue  # 跳过没有摘要的文章
                    
                similarity = self._calculate_advanced_similarity(paper_content, abstract)
                comparison_results.append({
                    'article_title': article['title'],
                    'similarity_rate': round(similarity, 2),
                    'url': article.get('url', f"https://www.semanticscholar.org/paper/{article.get('paperId', '')}"),
                    'authors': ', '.join([author['name'] for author in article.get('authors', [])])
                })
            
            # 6. 计算综合相似度
            avg_similarity = sum(res['similarity_rate'] for res in comparison_results) / max(1, len(comparison_results))
            Operation.log_operation(
                user_id=userid,
                paper_id=None,
                operation_type="查重",
                file_name="filename",
                operation_time=datatime.now()
            )
            
            # 7. 返回结果（确保数据结构完整性）
            return {
                'code': 200,
                'message': '查重完成（使用Semantic Scholar API）',
                'data': {
                    'comprehensive_similarity': round(avg_similarity, 2),
                    'paper_title': paper_title,
                    'comparison_results': comparison_results,
                    'keywords': keywords,
                    'num_articles': len(comparison_results),
                    'using_api': True
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
    def extract_theme(self, file):
        """论文主题提取（直接接收文件）"""
        try:
            # 1. 检查文件是否有效
            if not file or not file.filename:
                return {
                    'code': 400,
                    'message': '未上传有效文件'
                }
            
            # 2. 解析文件获取内容
            filename = file.filename
            file_ext = filename.split('.')[-1].lower()
            paper_content = self._extract_file_content(file, file_ext)
            
            if not paper_content:
                return {
                    'code': 400,
                    'message': '文件内容为空，无法提取主题'
                }
            
            # 3. 文本预处理
            processed_text = self.preprocess_text(paper_content)
            
            # 4. 提取关键词
            keywords = self.extract_keywords(paper_content, top_n=5)
            if not keywords:
                return {
                    'code': 400,
                    'message': '无法提取主题关键词'
                }
            
            # 5. 统计词频，获取高频词
            word_counts = Counter(processed_text)
            top_words = word_counts.most_common(20)  # 取前20个高频词
            
            # 6. 生成主题摘要
            theme_summary = self._generate_theme_summary(paper_content, keywords, top_words)
            
            # 7. 构建返回结果（从文件名获取标题）
            paper_title = filename.rsplit('.', 1)[0]  # 使用文件名作为标题

            result = {
                'title': paper_title,
                'keywords': keywords,
                'top_words': top_words,
                'summary': theme_summary,
                'word_frequency': dict(word_counts),
                'filename': filename
            }
            return {
                'code': 200,
                'message': '主题提取完成',
                'data': result
            }
            
        except Exception as e:
            current_app.logger.error(f'主题提取错误: {str(e)}')
            return {
                'code': 500,
                'message': f'主题提取失败: {str(e)}'
            }

    def _extract_file_content(self, file, file_ext):
        """从文件对象中提取内容（支持多种格式）"""
        try:
            # 读取文件字节数据
            file_bytes = file.read()
            
            if file_ext == 'txt':
                # 文本文件直接解码
                return file_bytes.decode('utf-8', errors='ignore')
            
            elif file_ext == 'pdf':
                # PDF文件解析（需要pdfplumber库）
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    return ''.join([page.extract_text() or '' for page in pdf.pages])
            
            elif file_ext == 'docx':
                # DOCX文件解析（基于XML的ZIP格式）
                from docx import Document
                doc = Document(io.BytesIO(file_bytes))
                return '\n'.join([para.text for para in doc.paragraphs])
        
            elif file_ext == 'doc':
                # DOC文件解析（二进制格式）
                import textract  # 需要安装textract库
                text = textract.process(io.BytesIO(file_bytes), extension='doc')
                return text.decode('utf-8', errors='ignore')
        
            else:
                # 不支持的文件格式
                current_app.logger.warning(f'不支持的文件格式: {file_ext}')
                return None
                
        except Exception as e:
            current_app.logger.error(f'文件解析错误: {str(e)}')
            return None


    def _generate_theme_summary(self, text, keywords, top_words, summary_length=500):
        """生成主题摘要"""
        # 1. 按句号、问号、感叹号分割段落
        logger.info("begin theme summary")
        paragraphs = re.split(r'(。|！|\?|\.|!|\?)', text)
        # 合并分割的标点符号和内容
        full_paragraphs = []
        for i in range(0, len(paragraphs), 2):
            if i + 1 < len(paragraphs):
                full_paragraphs.append(paragraphs[i] + paragraphs[i+1])
            else:
                full_paragraphs.append(paragraphs[i])
        
        # 2. 计算每个段落与关键词的相关度
        paragraph_scores = []
        for para in full_paragraphs:
            score = 0
            # 关键词出现次数越多，分数越高
            for keyword in keywords:
                score += para.count(keyword)
            # 高频词出现次数越多，分数越高
            for word, _ in top_words:
                score += para.count(word)
            paragraph_scores.append((para, score))
        
        # 3. 按分数排序，选择分数最高的段落作为摘要基础
        paragraph_scores.sort(key=lambda x: x[1], reverse=True)
        if not paragraph_scores:
            return "无法生成主题摘要"
        
        # 4. 截取前N个高分段落，合并为摘要
        selected_paragraphs = []
        current_length = 0
        for para, _ in paragraph_scores:
            para_length = len(para)
            if current_length + para_length <= summary_length:
                selected_paragraphs.append(para)
                current_length += para_length
            else:
                break
        
        # 5. 拼接摘要并处理长度
        summary = ''.join(selected_paragraphs)
        if len(summary) > summary_length:
            summary = summary[:summary_length] + '...'
        logger.error(f"end theme111111111 summary{summary!r}")
        return summary

