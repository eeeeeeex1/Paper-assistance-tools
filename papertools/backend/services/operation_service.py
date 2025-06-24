class OperationService:
    @staticmethod
    def record_operation(operation_type, user_id, paper_id=None):
        # 创建操作记录
        new_operation = Operation(operation_type=operation_type, user_id=user_id, paper_id=paper_id)
        db.session.add(new_operation)
        db.session.commit()
        return True, "操作记录成功"

    @staticmethod
    def get_operations_by_user(user_id):
        # 获取用户的所有操作记录
        operations = Operation.query.filter_by(user_id=user_id).all()
        return True, operations