# backend/routes/paper_route.py
from flask import Blueprint, request, jsonify
from service.paper_service import PaperService
from flasgger import swag_from,Swagger
from backend.models.user import  User
from backend.models.paper import Paper # 导入相关模型
import os

paper_bp = Blueprint('paper', __name__, url_prefix='/api/papers')
paper_service = PaperService()

@paper_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['论文管理'],
    'description': '获取所有论文',
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '页码'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 10, 'description': '每页数量'}
    ],
    'responses': {
        200: {
            'description': '成功获取论文列表',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '成功获取论文列表'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'papers': {
                                'type': 'array',
                                'items': {
                                    '$ref': '#/definitions/Paper'
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_all_papers():
    """获取所有论文（支持分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    # 实际应调用控制器方法，此处为示例
    return jsonify({
        'code': 200,
        'message': '成功获取论文列表',
        'data': {'papers': []}
    })

@paper_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['论文管理'],
    'description': '上传论文',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'required': True, 'description': '论文标题'},
                    'author_id': {'type': 'integer', 'required': True, 'description': '作者ID'},
                    'file_path': {'type': 'string', 'required': True, 'description': '论文文件路径'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': '论文上传成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 201},
                    'message': {'type': 'string', 'example': '论文上传成功'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'paper_id': {'type': 'integer'},
                            'title': {'type': 'string'},
                            'upload_time': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {'description': '缺少必要参数'},
        500: {'description': '上传失败'}
    }
})
def upload_paper():
    """上传新论文"""
    return paper_service.upload_paper()

@paper_bp.route('/<int:paper_id>', methods=['GET'])
@swag_from({
    'tags': ['论文管理'],
    'description': '获取单个论文信息',
    'parameters': [
        {'name': 'paper_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '论文ID'}
    ],
    'responses': {
        200: {
            'description': '成功获取论文信息',
            'schema': {
                '$ref': '#/definitions/PaperResponse'
            }
        },
        404: {'description': '论文不存在'}
    }
})
def get_paper(paper_id):
    """通过ID获取论文"""
    return paper_service.get_paper(paper_id)

@paper_bp.route('/<int:paper_id>', methods=['DELETE'])
@swag_from({
    'tags': ['论文管理'],
    'description': '删除论文',
    'parameters': [
        {'name': 'paper_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '论文ID'}
    ],
    'responses': {
        200: {
            'description': '删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '删除成功'}
                }
            }
        },
        400: {'description': '删除失败'},
        404: {'description': '论文不存在'}
    }
})
def delete_paper(paper_id):
    """删除论文"""
    return paper_service.delete_paper(paper_id)

@paper_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['论文管理'],
    'description': '获取用户的所有论文',
    'parameters': [
        {'name': 'user_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '用户ID'},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '页码'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 10, 'description': '每页数量'}
    ],
    'responses': {
        200: {
            'description': '成功获取用户论文列表',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '成功获取用户论文列表'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'user_info': {'$ref': '#/definitions/User'},
                            'papers': {
                                'type': 'array',
                                'items': {'$ref': '#/definitions/Paper'}
                            }
                        }
                    }
                }
            }
        },
        404: {'description': '用户不存在'}
    }
})
def get_user_papers(user_id):
    """获取指定用户的所有论文"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return paper_service.get_user_papers(user_id, page, per_page)

@paper_bp.route('/<int:paper_id>/spelling', methods=['GET'])
@swag_from({
    'tags': ['论文管理'],
    'description': '论文错字检测',
    'parameters': [
        {'name': 'paper_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '论文ID'}
    ],
    'responses': {
        200: {
            'description': '错字检测完成',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '错字检测完成'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'error_count': {'type': 'integer'},
                            'sample_errors': {'type': 'array', 'items': {'type': 'string'}},
                            'suggestions': {'type': 'array', 'items': {'type': 'string'}}
                        }
                    }
                }
            }
        },
        400: {'description': '检测失败'},
        404: {'description': '论文不存在'}
    }
})
def check_spelling(paper_id):
    """论文错字检测"""
    return paper_service.check_spelling(paper_id)

@paper_bp.route('/<int:paper_id>/plagiarism', methods=['GET'])
@swag_from({
    'tags': ['论文管理'],
    'description': '论文查重，计算与相似文章的综合相似度',
    'parameters': [
        {'name': 'paper_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '论文ID'},
        {'name': 'num_articles', 'in': 'query', 'type': 'integer', 'default': 5, 'description': '爬取的相似文章数量'}
    ],
    'responses': {
        200: {
            'description': '查重完成，返回相似度结果',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '查重完成'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'comprehensive_similarity': {'type': 'number', 'example': 25.63},
                            'paper_title': {'type': 'string', 'example': '人工智能在医疗中的应用'},
                            'keywords': {'type': 'array', 'example': ['人工智能', '医疗']},
                            'comparison_results': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'article_title': {'type': 'string'},
                                        'similarity_rate': {'type': 'number'},
                                        'url': {'type': 'string'}
                                    }
                                }
                            },
                            'most_similar_sections': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'paper_para': {'type': 'string'},
                                        'article_para': {'type': 'string'},
                                        'similarity': {'type': 'number'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {'description': '论文不存在'},
        400: {'description': '参数错误或内容为空'},
        500: {'description': '查重过程中服务器错误'}
    }
    })
def check_plagiarism(paper_id):
    """论文查重"""
    return paper_service.check_plagiarism(paper_id)

@paper_bp.route('/<int:paper_id>/theme', methods=['GET'])
@swag_from({
    'tags': ['论文管理'],
    'description': '主题提取',
    'parameters': [
        {'name': 'paper_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {
            'description': '成功，返回关键词和摘要',
            'examples': {
                'application/json': {
                    'code': 200,
                    'message': '主题提取完成',
                    'data': {
                        'keywords': ['人工智能', '医疗诊断'],
                        'summary': '本研究主要探讨了...'
                    }
                }
            }
        },
        404: {'description': '论文不存在'},
        400: {'description': '请求参数错误'}
    }
})
def extract_theme(paper_id):
    """论文主题提取"""
    return paper_service.extract_theme(paper_id)



