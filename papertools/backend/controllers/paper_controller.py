from flask import Blueprint, request, jsonify
from models import Paper, db, User

paper_bp = Blueprint('paper', __name__)

@paper_bp.route('/upload', methods=['POST'])
def upload_paper():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    user_id = data.get('user_id')

    new_paper = Paper(title=title, content=content, user_id=user_id)
    db.session.add(new_paper)
    db.session.commit()

    return jsonify({'message': '论文上传成功', 'paper_id': new_paper.id}), 201

@paper_bp.route('/papers', methods=['GET'])
def get_papers():
    user_id = request.args.get('user_id')
    papers = Paper.query.filter_by(user_id=user_id).all()
    paper_list = [{
        'id': paper.id,
        'title': paper.title,
        'upload_date': paper.upload_date,
        'theme': paper.theme,
        'similarity_score': paper.similarity_score
    } for paper in papers]

    return jsonify({'papers': paper_list}), 200