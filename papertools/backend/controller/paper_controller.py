# backend/routes/paper_route.py
from flask import Blueprint, request, jsonify,current_app
from service.paper_service import PaperService
from flasgger import swag_from,Swagger
from backend.models.user import  User
from dao.paper_dao import PaperDao
from backend.config.database import db
from backend.models.paper import Paper # 导入相关模型
import os
from config.logging_config import logger

paper_bp = Blueprint('paper', __name__, url_prefix='/api/paper')
paper_service=PaperService()

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


@paper_bp.route('/upload', methods=['POST'])
@swag_from({
    'tags': ['论文管理'],
    'description': '上传论文',
    'consumes': ['multipart/form-data'],  # 修改为表单数据
    'parameters': [
        {
            'name': 'title',
            'in': 'formData',  # 修改为 formData
            'type': 'string',
            'required': True,
            'description': '论文标题'
        },
        {
            'name': 'author_id',
            'in': 'formData',  # 修改为 formData
            'type': 'integer',
            'required': True,
            'description': '作者ID'
        },
        {
            'name': 'file',
            'in': 'formData',  # 添加文件参数
            'type': 'file',
            'required': True,
            'description': '论文文件'
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
    """上传论文并返回paper ID"""
    logger.info("begin upload paper")
    title = request.form.get('title')
    author_id = request.form.get('author_id', type=int)
    file = request.files.get('file')
    logger.info("all is rignt ")
    if not all([title, author_id, file]):
        return jsonify({"code": 400, "message": "缺少必要参数"}), 400
    
    try:
        paper = paper_service.upload_paper(title, author_id, file)
        return jsonify({
            "code": 201,  # 使用201表示创建成功
            "message": "上传成功",
            "data": {
                "paper_id": paper.id,
                "file_path": paper.file_path  # 可选：返回file_path（可能为空）
            }
        }), 201
        
    except ValueError as e:
        return jsonify({"code": 400, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"上传失败: {str(e)}")
        return jsonify({"code": 500, "message": "服务器处理失败"}), 500

@paper_bp.route('/getpaperinfo', methods=['GET'])
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


@paper_bp.route('/spelling', methods=['POST'])
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
def check_spelling():
    """论文错字检测（接收文件上传）"""
    logger.info("begin check spelling")
    
    # 从请求中获取文件
    if 'file' not in request.files:
        return jsonify({
            'code': 400,
            'message': '未上传文件'
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'code': 400,
            'message': '文件名为空'
        }), 400
    #获取查询参数
    user_id=request.form.get('user_id',type=int)
    
    # 调用服务层方法
    success, result = paper_service.check_spelling(file,user_id)
    logger.info("end check spelling")
    if success:
        return jsonify({
            'code': 200,
            'message': '错字检测完成',
            'data': result
        }), 200
    else:
        return jsonify({
            'code': 400,
            'message': result
        }), 400



@paper_bp.route('/plagiarism', methods=['POST'])
@swag_from({
    'tags': ['论文管理'],
    'description': '论文查重，直接上传文件计算相似度',
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '上传的论文文件'
        },
        {
            'name': 'num_articles',
            'in': 'formData',
            'type': 'integer',
            'default': 5,
            'description': '爬取的相似文章数量'
        }
    ],
    'responses': {
        200: {
            'description': '查重完成，返回相似度结果',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': 200,
                    'message': '查重完成',
                    'data': {
                        'comprehensive_similarity': 25.63,
                        'paper_title': '人工智能在医疗中的应用',
                        'keywords': ['人工智能', '医疗'],
                        # 其他字段...
                    }
                }
            }
        },
        400: {'description': '缺少文件或参数错误'},
        500: {'description': '服务器内部错误'}
    }
})
def check_plagiarism():
    logger.info("begin check plagiarism with file upload")

    # 获取上传的文件
    file = request.files.get('file')
    if not file:
        return jsonify({
            'code': 400,
            'message': '未上传论文文件',
            'data': None
        }), 400
    
    # 获取查询参数
    num_articles = request.form.get('num_articles', 5, type=int)
    user_id=request.form.get('user_id',type=int)
    try:
        # 调用服务层方法
        logger.info("begin controller check plagiarism")
        result = paper_service.check_plagiarism(file, num_articles,user_id)
        logger.info("end controller check plagiarism with file upload")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"查重失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '查重过程中服务器错误',
            'data': None
        }), 500

@paper_bp.route('/theme', methods=['POST'])
def extract_theme():
    logger.info("begin 111111 extract theme")
    
    if 'file' not in request.files:
        return jsonify({
            'code': 400,
            'message': '未上传文件'
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'code': 400,
            'message': '文件名为空'
        }), 400
    #获取查询参数
    user_id=request.form.get('user_id',type=int)
    try:
        # 调用服务层方法
        result = paper_service.extract_theme(file,user_id)
        return jsonify(result), result.get('code', 500)
    except Exception as e:
        # 记录详细的错误堆栈信息
        import traceback
        logger.error(f"调用服务层方法时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500
#-----------------------------------------------------------------------------------