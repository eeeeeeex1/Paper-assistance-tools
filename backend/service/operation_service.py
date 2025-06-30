# backend/controllers/operation_controller.py
from flask import request
from dao.operation_dao import OperationDao
from typing import Dict, Any, Optional, List
from config.logging_config import logger
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
    
    def get_user_operations(self, user_id, page=1, per_page=20):
        """获取用户的操作记录"""
        # 检查用户是否存在
        from backend.models.user import User
        user = User.query.get(user_id)
        if not user:
            return {
                'code': 404,
                'message': '用户不存在'
            }
        
        operations = self.operation_dao.get_operations_by_user(user_id, page, per_page)
        
        return {
            'code': 200,
            'message': '获取成功',
            'data': {
                'user_info': {
                    'user_id': user.id,
                    'username': user.username
                },
                'operations': [op.to_dict() for op in operations.items],
                'total': operations.total,
                'pages': operations.pages,
                'current_page': operations.page
                
            }
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
            
            if error:
                return {
                    'code': 400,
                    'message': error
                }
            
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
            
    #-------------------------------------------------------
    def get_operations(
        self,
        page: int = 1,
        per_page: int = 10,
        user_id: Optional[int] = None,
        paper_id: Optional[int] = None,
        operation_type: Optional[str] = None
    ) -> Dict[str, any]:
        """
        获取操作日志(Service层)
        :param include_relations: 是否加载关联数据
        :return: {
            'records': List[dict],
            'total': int,
            'pages': int,
            'current_page': int
        }
        """
        try:
            logger.info('begin service get operations')
            # 调用DAO层获取数据
            result = self.operation_dao.query_operations(
                page=page,
                per_page=per_page,
                user_id=user_id,
                paper_id=paper_id,
                operation_type=operation_type
            )
            logger.info('finish service get operations 111111')
            logger.info('result 的内容: %s', result)
            # 转换数据格式
            records = [{
                'id': op.id,
                'user_id': op.user_id,
                'paper_id': op.paper_id,
                'operation_type': op.operation_type,
                'operation_time': op.operation_time.isoformat(),
                'file_name': op.file_name
            } for op in result['items']]

            logger.info('finish service get operations 22222')
            logger.info("返回的操作记录数据: %s", records)
            logger.info(f'成功获取 {len(records)} 条操作记录')
            return {
                'records': records,
                'total': result['total'],
                'pages': result['pages'],
                'current_page': page
            }
            
        except ValueError as e:
            # 转换DAO层错误
            raise ValueError(f"服务层异常: {str(e)}")
        except Exception as e:
            # 处理其他异常
            raise RuntimeError(f"获取操作日志失败: {str(e)}")