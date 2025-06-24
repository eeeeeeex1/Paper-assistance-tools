from flask import Blueprint, request, jsonify
from models import Operation, db

operation_bp = Blueprint('operation', __name__)

@operation_bp.route('/record', methods=['POST'])
def record_operation():
    data = request.get_json()
    operation_type = data.get('operation_type')
    user_id = data.get('user_id')
    paper_id = data.get('paper_id')

    new_operation = Operation(operation_type=operation_type, user_id=user_id, paper_id=paper_id)
    db.session.add(new_operation)
    db.session.commit()

    return jsonify({'message': '操作记录成功'}), 201

@operation_bp.route('/operations', methods=['GET'])
def get_operations():
    user_id = request.args.get('user_id')
    operations = Operation.query.filter_by(user_id=user_id).all()
    operation_list = [{
        'id': operation.id,
        'operation_type': operation.operation_type,
        'timestamp': operation.timestamp,
        'paper_id': operation.paper_id
    } for operation in operations]

    return jsonify({'operations': operation_list}), 200