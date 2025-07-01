# backend/controllers/operation_controller.py
from flask import request
from backend.dao.operation_dao import OperationDao
from backend.models.operation import Operation
from backend.models.user import User
from typing import List, Dict, Tuple, Optional
from config.logging_config import logger
from flask import jsonify  # 添加导入
from config.database import db

class OperationService:
    def __init__(self):
        self.operation_dao = OperationDao()
    
    def get_operation(self, operation_id):
        """获取单个操作记录"""
        operation = self.operation_dao.get_operation_by_id(operation_id)
        
        if not operation:
            return {
                'code': 404,
                'message': '操作记录不存在'
            }
        
        return {
            'code': 200,
            'message': '获取成功',
            'data': operation.to_dict()
        }
    
    def get_paper_operations(self, paper_id, page=1, per_page=20):
        """获取论文的操作记录"""
        # 检查论文是否存在
        from backend.models import Paper
        paper = Paper.query.get(paper_id)
        if not paper:
            return {
                'code': 404,
                'message': '论文不存在'
            }
        
        operations = self.operation_dao.get_operations_by_paper(paper_id, page, per_page)
        
        return {
            'code': 200,
            'message': '获取成功',
            'data': {
                'paper_info': {
                    'paper_id': paper.id,
                    'title': paper.title
                },
                'operations': [op.to_dict() for op in operations.items],
                'total': operations.total,
                'pages': operations.pages,
                'current_page': operations.page
            }
        }
    
    def log_operation(self):
        """记录新操作"""
        try:
            # 获取请求参数
            logger.info("begin ao")
            logger.info("begin service")
            user_id = request.json.get('user_id')
            paper_id = request.json.get('paper_id')
            operation_type = request.json.get('operation_type')
            
            if not user_id or not operation_type:
                return {
                    'code': 400,
                    'message': '缺少必要参数(用户ID、操作类型)'
                }
            
            # 调用服务层记录操作
            operation, error = self.operation_dao.log_operation(user_id, paper_id, operation_type)
            logger.info("end service")
            if error:
                return {
                    'code': 400,
                    'message': error
                }
            logger.info("end dao")
            return {
                'code': 201,
                'message': '操作记录添加成功',
                'data': operation.to_dict()
            }
        except Exception as e:
            return {
                'code': 500,
                'message': f'记录操作失败: {str(e)}'
            }
    
    def get_operation_stats(self):
        """获取操作统计信息"""
        try:
            user_id = request.args.get('user_id', type=int)
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # 日期格式转换
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            
            stats = self.operation_dao.get_operation_stats(user_id, start, end)
            
            return {
                'code': 200,
                'message': '统计信息获取成功',
                'data': stats
            }
        except Exception as e:
            return {
                'code': 500,
                'message': f'获取统计信息失败: {str(e)}'
            }

    def get_user_operations(self, user_id, page=1, per_page=20):
        try:
            # 参数验证
            if page < 1:
                return jsonify({
                    'code': 400,
                    'message': '页码不能小于1'
                }), 400
            
            if per_page < 1 or per_page > 100:
                return jsonify({
                    'code': 400,
                    'message': '每页记录数范围为1-100'
                }), 400
            
            logger.info(f'开始查询用户 {user_id} 的操作记录，页码: {page}, 每页: {per_page}')
            
            # 调用DAO获取原始分页数据
            operations = self.operation_dao.get_user_operations(user_id, page, per_page)
            
            # 输出总记录数和当前页记录数
            logger.info(f'查询完成，总记录数: {operations.total}, 当前页记录数: {len(operations.items)}')
        
            # 输出当前页的操作记录详情（只输出前5条，避免日志过多）
            logger.info('当前页操作记录详情:')
            for i, op in enumerate(operations.items[:5]):
                logger.info(f'记录 {i+1}: {op.to_dict()}')
        
            if len(operations.items) > 5:
                logger.info(f'  ... 还有 {len(operations.items) - 5} 条记录未显示')
            # 转换为字典列表
            operation_list = [op.to_dict() for op in operations.items]
            
            # 构建响应
            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'total': operations.total,
                    'pages': operations.pages,
                    'current_page': operations.page,
                    'per_page': per_page,
                    'operations': operation_list
                }
            })
            
        except Exception as e:
            logger.error(f'获取用户操作记录失败: {str(e)}', exc_info=True)
            db.session.rollback()
            return jsonify({
                'code': 500,
                'message': f'获取操作记录失败: {str(e)}'
            }), 500
    
    def delete_operation(self, operation_id):
        """删除操作记录"""
        success, error = self.operation_dao.delete_operation(operation_id)
        if success:
            return {
                'code': 200,
                'message': '操作记录删除成功'
            }
        else:
            return {
                'code': 400,
                'message': error
            }