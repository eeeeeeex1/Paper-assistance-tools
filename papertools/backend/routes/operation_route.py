from flask import Blueprint, request, jsonify
from services.operation_service import OperationService

operation_bp = Blueprint('operation', __name__)

@operation_bp.route('/record', methods=['POST'])
def record_operation():
    data = request.get_json()
    operation_type = data.get('operation_type')
    user_id = data.get('user_id')
    paper_id = data.get('paper_id')

    success, message = OperationService.record_operation(operation_type, user_id, paper_id)
    if success:
        return jsonify({'message': message}), 201
    else:
        return jsonify({'message': message}), 400

@operation_bp.route('/operations', methods=['GET'])
def get_operations():
    user_id = request.args.get('user_id')
    success, operations = OperationService.get_operations_by_user(user_id)
    if success:
        operation_list = [{
            'id': operation.id,
            'operation_type': operation.operation_type,
            'timestamp': operation.timestamp,
            'user_id': operation.user_id,
            'paper_id': operation.paper_id
        } for operation in operations]
        return jsonify({'operations': operation_list}), 200
    else:
        return jsonify({'message': '用户不存在'}), 404