# backend/routes/operation_route.py
from flask import Blueprint, request, jsonify
from service.operation_service import OperationService
from flasgger import swag_from,Swagger
from backend.models.operation import Operation
from backend.models.user import  User
from backend.models.paper import Paper # 导入相关模型
from backend.models.operation import Operation
import os
from config.logging_config import logger
# 创建操作记录模块的蓝图
operation_bp = Blueprint('operation', __name__, url_prefix='/api/operations')

# 初始化控制器
operation_service = OperationService()

# === 操作记录API路由 ===

@operation_bp.route('/<int:operation_id>', methods=['GET'])
@swag_from({
    'tags': ['日志管理'],
    'description': '获取单个操作记录',
    'parameters': [
        {'name': 'operation_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '操作记录ID'}
    ],
    'responses': {
        200: {
            'description': '成功获取操作记录',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '获取成功'},
                    'data': {
                        '$ref': '#/definitions/Operation'
                    }
                }
            }
        },
        404: {'description': '操作记录不存在'}
    }
})
def get_operation(operation_id):
    """通过ID获取操作记录"""
    return operation_service.get_operation(operation_id)


@operation_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['日志管理'],
    'description': '获取用户的操作记录',
    'parameters': [
        {'name': 'user_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '用户ID'},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '页码'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 20, 'description': '每页数量'}
    ],
    'responses': {
        200: {
            'description': '成功获取用户操作记录',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '获取成功'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'user_info': {'$ref': '#/definitions/User'},
                            'operations': {
                                'type': 'array',
                                'items': {'$ref': '#/definitions/Operation'}
                            },
                            'total': {'type': 'integer'},
                            'pages': {'type': 'integer'},
                            'current_page': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        404: {'description': '用户不存在'}
    }
})
def get_user_operations(user_id):
    """获取用户的所有操作记录"""
    logger.info("begin controller getoperaitons")
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return operation_service.get_user_operations(user_id, page, per_page)

@operation_bp.route('/paper/<int:paper_id>', methods=['GET'])
@swag_from({
    'tags': ['日志管理'],
    'description': '获取论文的操作记录',
    'parameters': [
        {'name': 'paper_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '论文ID'},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '页码'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 20, 'description': '每页数量'}
    ],
    'responses': {
        200: {
            'description': '成功获取论文操作记录',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '获取成功'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'paper_info': {'$ref': '#/definitions/Paper'},
                            'operations': {
                                'type': 'array',
                                'items': {'$ref': '#/definitions/Operation'}
                            },
                            'total': {'type': 'integer'},
                            'pages': {'type': 'integer'},
                            'current_page': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        404: {'description': '论文不存在'}
    }
})
def get_paper_operations(paper_id):
    """获取论文的所有操作记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return operation_service.get_paper_operations(paper_id, page, per_page)

@operation_bp.route('/log', methods=['POST'])
@swag_from({
    'tags': ['日志管理'],
    'description': '记录新操作',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer', 'required': True, 'description': '用户ID'},
                    'paper_id': {'type': 'integer', 'description': '论文ID'},
                    'operation_type': {'type': 'string', 'required': True, 'description': '操作类型'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': '操作记录添加成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 201},
                    'message': {'type': 'string', 'example': '操作记录添加成功'},
                    'data': {'$ref': '#/definitions/Operation'}
                }
            }
        },
        400: {'description': '缺少必要参数'},
        500: {'description': '记录操作失败'}
    }
})
def log_operation():
    """记录新的操作"""
    logger.info('begin log_operation')
    return operation_service.log_operation()

@operation_bp.route('/stats', methods=['GET'])
@swag_from({
    'tags': ['日志管理'],
    'description': '获取操作统计信息',
    'parameters': [
        {'name': 'user_id', 'in': 'query', 'type': 'integer', 'description': '用户ID'},
        {'name': 'start_date', 'in': 'query', 'type': 'string', 'description': '开始日期 (YYYY-MM-DD)'},
        {'name': 'end_date', 'in': 'query', 'type': 'string', 'description': '结束日期 (YYYY-MM-DD)'}
    ],
    'responses': {
        200: {
            'description': '成功获取操作统计信息',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '统计信息获取成功'},
                    'data': {
                        'type': 'object',
                        'description': '操作类型到数量的映射'
                    }
                }
            }
        },
        500: {'description': '获取统计信息失败'}
    }
})
def get_operation_stats():
    """获取操作统计信息"""
    return operation_service.get_operation_stats()

@operation_bp.route('/<int:operation_id>', methods=['DELETE'])
@swag_from({
    'tags': ['日志管理'],
    'description': '删除操作记录',
    'parameters': [
        {'name': 'operation_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '操作记录ID'}
    ],
    'responses': {
        200: {
            'description': '操作记录删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '操作记录删除成功'}
                }
            }
        },
        400: {'description': '删除操作记录失败'}
    }
})
def delete_operation(operation_id):
    """删除操作记录"""
    return operation_service.delete_operation(operation_id)

    #----------------------------------------------------------

@operation_bp.route('/getall', methods=['GET'])
@operation_bp.route('/getall/user/<int:user_id>', methods=['GET'])
@operation_bp.route('/getall/paper/<int:paper_id>', methods=['GET'])
def get_operations(user_id=None, paper_id=None):
    try:
        logger.info('begin operation get all')
        # 参数校验
        page = max(1, request.args.get('page', 1, type=int))
        per_page = min(max(1, request.args.get('per_page', 10, type=int)), 100)
        operation_type = request.args.get('operation', None)
        
        # 调用Service层
        data = operation_service.get_operations(
            page=page,
            per_page=per_page,
            user_id=user_id,
            paper_id=paper_id,
            operation_type=operation_type
        )
        logger.info('finish operation get all')
        return jsonify({
            'status': 'success',
            'data': data
        })
        
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500
    
#lmk----------------------------------------------------------------
@operation_bp.route('/type_count', methods=['GET'])
def get_operation_type_count():
    """获取操作类型统计接口"""
    logger.info('get front request')
    try:
        data = OperationService.get_operation_type_count()
        return jsonify({
            'code': 200,
            'message': '获取操作类型统计成功',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取操作类型统计失败: {str(e)}'
        }), 500
#lmk-----------------------------------------------------------------------