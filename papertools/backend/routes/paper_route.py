from flask import Blueprint, request, jsonify
from services.paper_service import PaperService

paper_bp = Blueprint('paper', __name__)

@paper_bp.route('/upload', methods=['POST'])
def upload_paper():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    user_id = data.get('user_id')

    success, message, paper = PaperService.upload_paper(title, content, user_id)
    if success:
        return jsonify({'message': message, 'paper_id': paper.id}), 201
    else:
        return jsonify({'message': message}), 400

@paper_bp.route('/papers', methods=['GET'])
def get_papers():
    user_id = request.args.get('user_id')
    success, papers = PaperService.get_papers_by_user(user_id)
    if success:
        paper_list = [{
            'id': paper.id,
            'title': paper.title,
            'upload_date': paper.upload_date,
            'theme': paper.theme,
            'similarity_score': paper.similarity_score
        } for paper in papers]
        return jsonify({'papers': paper_list}), 200
    else:
        return jsonify({'message': '用户不存在'}), 404

@paper_bp.route('/paper/<int:paper_id>', methods=['GET'])
def get_paper(paper_id):
    paper = Paper.query.get(paper_id)
    if paper:
        return jsonify({
            'id': paper.id,
            'title': paper.title,
            'content': paper.content,
            'upload_date': paper.upload_date,
            'user_id': paper.user_id,
            'theme': paper.theme,
            'similarity_score': paper.similarity_score
        }), 200
    else:
        return jsonify({'message': '论文不存在'}), 404