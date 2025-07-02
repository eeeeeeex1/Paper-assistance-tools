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
        }), 500