# backend/controller/ai_controller.py
from flask import Blueprint, request, jsonify,current_app
from backend.service.xinghuo_service import XinghuoService
from backend.models.operation import Operation
from datetime import datetime
from backend.utils.file_utils import read_file_content

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/theme_extraction', methods=['POST'])
def theme_extraction():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'message': '未上传文件'
            }), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'code': 400,
                'message': '未选择文件'
            }), 400
            
        # 读取文件内容
        file_content = read_file_content(file)
        if not file_content:
            return jsonify({
                'code': 400,
                'message': '文件内容为空'
            }), 400
            
        # 获取用户ID
        user_id = request.form.get('user_id') or 'default_user'
        
        # 调用主题提取服务
        xinghuo_service = XinghuoService()
        result = xinghuo_service.extract_theme(file_content, file.filename, user_id)
        
        if result:
            return jsonify({
                'code': 200,
                'message': '主题提取成功',
                'data': result
            })
        else:
            return jsonify({
                'code': 500,
                'message': '主题提取失败，未获取到有效结果'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"主题提取出错: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500