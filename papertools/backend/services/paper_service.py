class PaperService:
    @staticmethod
    def upload_paper(title, content, user_id):
        # 创建新论文
        new_paper = Paper(title=title, content=content, user_id=user_id)
        db.session.add(new_paper)
        db.session.commit()
        return True, "论文上传成功", new_paper

    @staticmethod
    def get_papers_by_user(user_id):
        # 获取用户的所有论文
        papers = Paper.query.filter_by(user_id=user_id).all()
        return True, papers

    @staticmethod
    def analyze_paper_similarity(paper_id1, paper_id2):
        # 获取论文内容
        paper1 = Paper.query.get(paper_id1)
        paper2 = Paper.query.get(paper_id2)
        if not paper1 or not paper2:
            return False, "论文不存在"
        
        # 调用 NLP 模块进行相似度分析
        similarity_score = analyze_similarity(paper1.content, paper2.content)
        return True, similarity_score

    @staticmethod
    def extract_paper_theme(paper_id):
        # 获取论文内容
        paper = Paper.query.get(paper_id)
        if not paper:
            return False, "论文不存在"
        
        # 调用 NLP 模块提取主题
        theme = extract_theme(paper.content)
        return True, theme