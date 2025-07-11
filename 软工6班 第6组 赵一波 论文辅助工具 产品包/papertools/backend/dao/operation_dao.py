# backend/services/operation_service.py
from backend.models.operation import Operation
from backend.models.user import User
from backend.config.database import db
import logging
from datetime import datetime, timedelta
from config.logging_config import logger
from sqlalchemy import desc  # 缺少这行导入
from typing import Dict, Any, Optional, List
#lmk-----------------------------------------------
from sqlalchemy import func
#lmk------------------------------------------------

# 初始化日志记录器
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class OperationDao:
    def get_operation_by_id(self, operation_id):
        """通过ID获取操作记录"""
        return Operation.query.get(operation_id)
    
    def get_operations_by_user(self, user_id, page=1, per_page=20):
        """获取用户的操作记录（支持分页）"""
        return Operation.query.filter_by(user_id=user_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def get_operations_by_paper(self, paper_id, page=1, per_page=20):
        """获取与论文相关的操作记录（支持分页）"""
        return Operation.query.filter_by(paper_id=paper_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def get_recent_operations(self, days=7, page=1, per_page=20):
        """获取最近N天的操作记录(支持分页)"""
        start_time = datetime.utcnow() - timedelta(days=days)
        return Operation.query.filter(
            Operation.operation_time >= start_time
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    def log_operation(self, user_id, paper_id, operation_type):
        """记录新的操作"""
        try:
            # 检查用户是否存在
            from backend.models import User
            user = User.query.get(user_id)
            if not user:
                return None, "用户不存在"
            
            # 记录操作
            operation = operation.log_operation(user_id, paper_id, operation_type)
            return operation, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"记录操作失败: {str(e)}")
            return None, f"记录操作失败: {str(e)}"
    
    def get_operation_stats(self, user_id=None, start_date=None, end_date=None):
        """获取操作统计信息"""
        query = Operation.query
        
        # 按用户过滤
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # 按时间范围过滤
        if start_date and end_date:
            query = query.filter(
                Operation.operation_time >= start_date,
                Operation.operation_time <= end_date
            )
        
        # 统计各操作类型的数量
        from sqlalchemy.sql import func
        stats = query.with_entities(
            Operation.operation_type,
            func.count(Operation.operation_type).label('count')
        ).group_by(Operation.operation_type).all()
        
        return {stat.operation_type: stat.count for stat in stats}
#-----------------------------------------------------------------------
    
    def get_user_operations(self,user_id, page, per_page):
        """获取用户的操作记录（带分页），返回原始Pagination对象"""
        try:
            query = Operation.query.filter_by(user_id=user_id).order_by(desc(Operation.operation_time))
            return query.paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            raise e  # 抛出异常，由Service层处理
    def delete_operation(self, operation_id):
        """删除操作记录"""
        try:
            operation = Operation.query.get(operation_id)
            if operation:
                db.session.delete(operation)
                db.session.commit()
                return True, None
            else:
                return False, "操作记录不存在"
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除操作记录失败: {str(e)}")
            return False, f"删除操作记录失败: {str(e)}"


    
        #-----------------------------------------------------
    def query_operations(
        self,
        page: int = 1,
        per_page: int = 10,
        user_id: Optional[int] = None,
        paper_id: Optional[int] = None,
        operation_type: Optional[str] = None
    ) -> Dict[str, any]:
        """
        基础查询方法（DAO层）
        :return: {
            'items': List[Operation], 
            'total': int,
            'pages': int
        }
        """
        try:
            logger.info('begin dao find`operations')
            query = Operation.query
            
            # 条件过滤
            if user_id:
                query = query.filter(Operation.user_id == user_id)
            if paper_id:
                query = query.filter(Operation.paper_id == paper_id)
            if operation_type:
                query = query.filter(Operation.operation_type == operation_type)
            logger.info('1111111111')
            # 执行分页查询
            pagination = query.order_by(
                desc(Operation.operation_time)
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            logger.info('finish dao find`operations')
            return {
                'items': pagination.items,
                'total': pagination.total,
                'pages': pagination.pages
            }
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"数据库查询失败: {str(e)}")

            #lmk---------------------------------------------------------------------
    @staticmethod
    def get_operation_type_count():
        try:
            result = db.session.query(
                Operation.operation_type,
                func.count(Operation.id).label('count')
            ).group_by(Operation.operation_type).all()
            
            operation_types = ["similaritycheck", "spellcheck", "textsummary"]
            type_count = {type_: 0 for type_ in operation_types}
            
            for type_, count in result:
                if type_ in type_count:
                    type_count[type_] = count
                    
            return type_count
        finally:
            db.session.close()  # 确保会话关闭
#lmk---------------------------------------------------------------------