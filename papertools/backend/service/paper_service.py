# backend/controllers/paper_controller.py
from flask import current_app, request
from dao.paper_dao import PaperDao

class PaperService:
    def __init__(self):
        self.paper_dao = PaperDao()
    
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
        from backend.models import User
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
    
    def upload_paper(self):
        """上传论文"""
        try:
            # 获取请求参数
            title = request.json.get('title')
            author_id = request.json.get('author_id')
            file_path = request.json.get('file_path')  # 实际应用中可能通过文件上传获取
            
            if not title or not author_id or not file_path:
                return {
                    'code': 400,
                    'message': '缺少必要参数（标题、作者ID、文件路径）'
                }
            
            # 调用服务层上传论文
            paper, error = self.paper_dao.upload_paper(title, author_id, file_path)
            
            if error:
                return {
                    'code': 400,
                    'message': error
                }
            
            return {
                'code': 201,
                'message': '论文上传成功',
                'data': {
                    'paper_id': paper.id,
                    'title': paper.title,
                    'upload_time': paper.upload_time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        except Exception as e:
            return {
                'code': 500,
                'message': f'上传论文失败: {str(e)}'
            }
    
    def delete_paper(self, paper_id):
        """删除论文"""
        success, message = self.paper_dao.delete_paper(paper_id)
        
        if not success:
            return {
                'code': 400,
                'message': message
            }
        
        return {
            'code': 200,
            'message': message
        }
    
    def check_spelling(self, paper_id):
        """论文错字检测"""
        success, result = self.paper_dao.check_spelling(paper_id)
        
        if not success:
            return {
                'code': 400,
                'message': result
            }
        
        return {
            'code': 200,
            'message': '错字检测完成',
            'data': result
        }

    async def check_plagiarism(paper_id, num_articles=5):
        """
        论文查重：获取目标论文，爬取多篇主题相似文章，计算综合相似度
        num_articles: 爬取的相似文章数量（默认5篇）
        """
        # 1. 获取目标论文信息
        paper = Paper.query.get(paper_id)
        if not paper:
            return {
                'code': 404,
                'message': '论文不存在',
                'data': None
            }
        
        paper_title = paper.title
        paper_content = paper.content
        
        if not paper_content:
            return {
                'code': 400,
                'message': '论文内容为空，无法查重',
                'data': None
            }
        
        try:
            # 2. 提取论文主题关键词
            keywords = extract_keywords(paper_title)
            if not keywords:
                return {
                    'code': 400,
                    'message': '无法提取主题关键词',
                    'data': None
                }
            
            # 3. 异步爬取多篇相似文章
            similar_articles = await crawl_multiple_articles(keywords, num_articles)
            if not similar_articles:
                return {
                    'code': 400,
                    'message': '未找到相似文章，无法查重',
                    'data': None
                }
            
            # 4. 文本预处理
            processed_paper = preprocess_text(paper_content)
            
            # 5. 计算与每篇文章的相似度
            comparison_results = []
            all_similar_sections = []
            
            for article in similar_articles:
                article_content = article.get('content', '')
                if not article_content:
                    continue
                    
                processed_article = preprocess_text(article_content)
                similarity = calculate_similarity(processed_paper, processed_article)
                
                # 查找相似段落
                similar_sections = find_similar_sections(paper_content, article_content)
                all_similar_sections.extend(similar_sections)
                
                comparison_results.append({
                    'article_title': article.get('title', '未知'),
                    'similarity_rate': similarity,
                    'url': article.get('url', '')
                })
            
            # 6. 计算综合相似度（加权平均）
            if comparison_results:
                total_similarity = sum(res['similarity_rate'] for res in comparison_results)
                avg_similarity = total_similarity / len(comparison_results)
            else:
                avg_similarity = 0
            
            # 7. 生成结果（按相似度降序排列）
            comparison_results.sort(key=lambda x: x['similarity_rate'], reverse=True)
            all_similar_sections.sort(key=lambda x: x['similarity'], reverse=True)
            
            result = {
                'comprehensive_similarity': round(avg_similarity, 2),  # 综合相似度
                'paper_title': paper_title,
                'comparison_results': comparison_results,  # 每篇文章的对比结果
                'most_similar_sections': all_similar_sections[:5],  # 前5个最相似段落
                'keywords': keywords,
                'num_articles': len(similar_articles)
            }
            
            return {
                'code': 200,
                'message': '查重完成',
                'data': result
            }
            
        except Exception as e:
            return {
                'code': 500,
                'message': f'查重过程出错：{str(e)}',
                'data': None
            }

    
    def extract_theme(self, paper_id):
        """论文主题提取"""
        # 1. 获取论文内容
        paper = self.paper_dao.get_paper_by_id(paper_id)
        if not paper:
            return {
                'code': 404,
                'message': '论文不存在'
            }
        
        paper_content = paper.content
        if not paper_content:
            return {
                'code': 400,
                'message': '论文内容为空，无法提取主题'
            }
        
        try:
            # 2. 文本预处理
            processed_text = self.preprocess_text(paper_content)
            
            # 3. 提取关键词（使用已有辅助函数）
            keywords = self.extract_keywords(paper_content, top_n=5)
            if not keywords:
                return {
                    'code': 400,
                    'message': '无法提取主题关键词'
                }
            
            # 4. 统计词频，获取主题相关高频词
            word_counts = Counter(processed_text)
            top_words = word_counts.most_common(20)  # 取前20个高频词
            
            # 5. 生成主题摘要（基于关键词和高频词）
            theme_summary = self._generate_theme_summary(paper_content, keywords, top_words)
            
            # 6. 构建返回结果
            result = {
                'title': paper.title,
                'keywords': keywords,
                'top_words': top_words,
                'summary': theme_summary,
                'word_frequency': dict(word_counts)
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
    def _generate_theme_summary(self, text, keywords, top_words, summary_length=150):
        """生成主题摘要"""
        # 1. 按句号、问号、感叹号分割段落
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
        
        return summary

#---------------------------------------------------------------------------

### 辅助函数：主题关键词提取
    def extract_keywords(text, top_n=3):
        """使用jieba提取文本中的关键词"""
        # 去除标点符号和特殊字符
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
        # 分词
        words = jieba.cut(text)
        # 过滤停用词（需提前准备停用词表）
        stop_words = set(['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己'])
        filtered_words = [word for word in words if word and word not in stop_words]
        # 统计词频并取前n个
        word_counts = Counter(filtered_words)
        return [word for word, _ in word_counts.most_common(top_n)]
        
            
    ### 辅助函数：爬虫获取相似文章（以百度学术为例）
    def crawl_similar_article(keywords):
        """根据关键词爬取一篇主题相似的文章"""
        try:
            # 拼接搜索URL（百度学术）
            search_keywords = '+'.join(keywords)
            url = f'https://xueshu.baidu.com/s?wd={search_keywords}&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_from=&sc_as_para=sc_lib%3A'
            
            # 发送请求（添加请求头模拟浏览器）
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找第一篇文章的标题和链接
            article = {}
            
            # 提取标题（示例：百度学术的标题选择器）
            title_elem = soup.find('h3', class_='t c_font')
            if title_elem:
                article['title'] = title_elem.text.strip()
                link = title_elem.find('a', href=True)
                if link:
                    article['url'] = link['href']
            
            # 如果获取到链接，进一步爬取文章内容
            if 'url' in article:
                # 处理百度学术的重定向链接
                if article['url'].startswith('/'):
                    article['url'] = 'https://xueshu.baidu.com' + article['url']
                
                # 发送请求获取文章详情
                article_response = requests.get(article['url'], headers=headers, timeout=15)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 提取文章内容（示例：假设内容在class为'content'的元素中）
                content_elem = article_soup.find('div', class_='content')
                if content_elem:
                    article['content'] = content_elem.text.strip()
                else:
                    # 备选：从摘要中提取
                    abstract_elem = article_soup.find('div', class_='abstract_content')
                    article['content'] = abstract_elem.text.strip() if abstract_elem else "无法提取文章内容"
            else:
                # 未获取到链接时，使用搜索结果中的摘要
                abstract_elem = soup.find('div', class_='content-right_8Zs40')
                article['content'] = abstract_elem.text.strip() if abstract_elem else "无法提取文章内容"
            
            return article
        
        except Exception as e:
            print(f"爬虫出错: {str(e)}")
            return None

                

    ### 辅助函数：文本预处理
    def preprocess_text(text):
        """清洗文本、分词、去除停用词"""
        if not text:
            return []
        
        # 去除标点符号和特殊字符
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
        # 分词
        words = jieba.cut(text)
        # 过滤停用词
        stop_words = set(['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己'])
        return [word for word in words if word and word not in stop_words]


    ### 辅助函数：计算文本相似度（余弦相似度）
    def calculate_similarity(text1, text2):
        """使用余弦相似度计算两篇文章的相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 合并所有词，创建词袋
        all_words = list(set(text1 + text2))
        
        # 生成词频向量
        def get_word_vector(words):
            vector = []
            for word in all_words:
                vector.append(words.count(word))
            return vector
        
        vec1 = get_word_vector(text1)
        vec2 = get_word_vector(text2)
        
        # 计算点积
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        # 计算模长
        mag1 = math.sqrt(sum(a**2 for a in vec1))
        mag2 = math.sqrt(sum(b**2 for b in vec2))
        # 避免除零错误
        if mag1 * mag2 == 0:
            return 0.0
        # 计算余弦相似度
        similarity = dot_product / (mag1 * mag2)
        # 转换为百分比并保留两位小数
        return round(similarity * 100, 2)


    ### 辅助函数：查找相似段落
    def find_similar_sections(text1, text2, window_size=200):
        """查找两篇文章中的相似段落（简化版）"""
        if not text1 or not text2:
            return []
        
        similar_sections = []
        # 将文本分割成段落
        paragraphs1 = re.split(r'\n|\。|\！|\？|\.|!|\?', text1)
        paragraphs2 = re.split(r'\n|\。|\！|\？|\.|!|\?', text2)
        
        for para1 in paragraphs1:
            if len(para1) < 50:  # 跳过太短的段落
                continue
            for para2 in paragraphs2:
                if len(para2) < 50:
                    continue
                # 预处理段落
                proc_para1 = preprocess_text(para1)
                proc_para2 = preprocess_text(para2)
                # 计算段落相似度
                para_sim = calculate_similarity(proc_para1, proc_para2)
                # 如果相似度超过阈值，记录相似段落
                if para_sim > 30:  # 相似度阈值
                    similar_sections.append({
                        'paper_para': para1[:window_size] + '...',
                        'article_para': para2[:window_size] + '...',
                        'similarity': round(para_sim, 2)
                    })
                    # 为避免重复匹配，找到一个相似段落后跳出循环
                    break
        
        # 按相似度降序排序
        similar_sections.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_sections[:5]  # 返回前5个最相似的段落
#---------------------------------------------------------------------