<<<<<<< HEAD
# backend/controller/ai_controller.py
from flask import Blueprint, request, jsonify
from backend.service.xinghuo_service import XinghuoService
import logging
from datetime import datetime

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger('ai_controller')
xinghuo_service = XinghuoService()

@ai_bp.route('/api/ai/theme_extraction', methods=['POST'])
def theme_extraction():
    """使用星火X1 HTTP接口进行主题总结"""
    try:
        data = request.json
        content = data.get('content')
        file_name = data.get('file_name', '未知文件')
        user_id = data.get('user_id')
        parameters = data.get('parameters', {})
        
        # 验证输入
        if not content:
            return jsonify({
                "code": 400,
                "message": "缺少必要的文本内容参数"
            }), 400
        
        logger.info(f"主题提取请求 - 用户: {user_id}, 文件名: {file_name}")
        
        # 调用主题提取服务
        summary = xinghuo_service.generate_theme_summary(content, parameters)
        
         # 验证返回结果的完整性
        if not all(key in summary for key in ["title", "keywords", "summary"]):
            logger.warning("返回结果缺少必要字段，已补充默认值")
            summary = {
                "title": summary.get("title", "未提取到主题标题"),
                "keywords": summary.get("keywords", []),
                "summary": summary.get("summary", "未提取到主题概述"),
                "top_words": summary.get("top_words", [])
            }
            
        # 返回结果
        return jsonify({
            "code": 200,
            "message": "主题提取成功",
            "data": {
                **summary,
                "original_length": len(content),
                "file_name": file_name,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "model_used": "Spark X1"
            }
        })
        
    except ValueError as ve:
        logger.error(f"参数验证错误: {str(ve)}")
        return jsonify({
            "code": 400,
            "message": str(ve)
        }), 400
        
    except Exception as e:
        logger.error(f"主题提取失败: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"主题提取失败: {str(e)}"
=======
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
>>>>>>> 84e04e8417d89e505f829c5651864ed0aa6a7627
        }), 500