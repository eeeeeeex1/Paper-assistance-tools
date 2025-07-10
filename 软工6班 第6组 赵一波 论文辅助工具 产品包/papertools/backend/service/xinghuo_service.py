# backend/service/xinghuoservice.py (兼容OpenAI 1.0.0+)
import os
import json
import logging
from typing import Dict, Any
import openai
from openai import OpenAI, OpenAIError
from config.config import XINGHUO_APP_ID,XINGHUO_API_KEY,XINGHUO_API_PASSWORD
from models.operation import Operation
from datetime import datetime, timedelta,timezone

logger = logging.getLogger('xinghuo_service')


class XinghuoService:
    def __init__(self):
        api_password = os.getenv("XINGHUO_API_PASSWORD")
        if not api_password:
            error_msg = "缺少XINGHUO_API_PASSWORD环境变量"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.client = OpenAI(
            api_key=api_password,
            base_url="https://spark-api-open.xf-yun.com/v2"
        )
        
        logger.info("星火X1 HTTP服务初始化完成")
    
    def generate_theme_summary(self, content: str,  file_name, user_id, paper_id,parameters: dict = None) -> Dict[str, Any]:
        try:
            # 设置默认参数
            default_params = {
                "model": "x1",
                "temperature": 0.3,
                "max_tokens": 4096,
                "stream": False
            }
            
            if parameters:
                # 确保用户没有传入错误的model参数
                if "model" in parameters and parameters["model"] != "x1":
                    logger.warning(f"忽略无效的model参数: {parameters['model']}，使用正确的'x1'")
                    parameters.pop("model")
                default_params.update(parameters)
            
            # 构建提示词
            prompt = f"""请对以下文本进行专业主题总结，**必须返回严格的JSON格式**，确保可以被Python的json.loads()解析：
            {{
            "title": "核心主题标题（不超过20字）",
            "keywords": ["3-5个精准关键词", "按重要性排序"],
            "summary": "主题概述（300字内，涵盖所有主要观点）",
            "top_words": [["词汇", 出现次数], ["词汇", 次数]]
            }}

            注意：
            1. 确保JSON格式正确，无语法错误
            2. 不包含任何JSON之外的内容
            3. 数字类型字段（如次数）必须为整数
            
            文本内容：
            {content}"""
            
            logger.debug(f"发送请求到星火X1 API: {prompt[:200]}...")
            
            # 使用新的客户端接口调用API
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                **default_params
            )
            
            logger.debug(f"收到星火X1 API响应: {response}")
            Operation.log_operation(
                user_id=user_id,
                paper_id=paper_id,
                operation_type="textsummary",
                file_name=file_name,
                operation_time=datetime.now()
            )

            return self._parse_response(response)
            
        except OpenAIError as e:
            # 错误处理
            error_info = {
                "code": e.status_code if hasattr(e, "status_code") else "未知错误码",
                "message": str(e)
            }
            
            if hasattr(e, "response") and e.response:
                try:
                    error_data = e.response.json()
                    error_info.update({
                        "code": error_data.get("code", error_info["code"]),
                        "message": error_data.get("message", error_info["message"])
                    })
                except Exception as parse_error:
                    logger.warning(f"解析错误响应失败: {parse_error}")
            
            logger.error(f"星火API错误 {error_info['code']}: {error_info['message']}")
            raise Exception(f"API错误 {error_info['code']}: {error_info['message']}")
        
        except Exception as e:
            logger.error(f"主题提取失败: {str(e)}", exc_info=True)
            raise
    
    def _parse_response(self, response: Any) -> Dict[str, Any]:
        try:
            content = response.choices[0].message.content
        
            # 预处理：移除多余换行和空格（针对星火模型可能返回的不规范格式）
            cleaned_content = " ".join(content.split())
        
            # 尝试解析JSON
            if cleaned_content.startswith("{") and cleaned_content.endswith("}"):
                return json.loads(cleaned_content)
        
            # 提取JSON部分（处理前后有非JSON内容的情况）
            start_idx = cleaned_content.find("{")
            end_idx = cleaned_content.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_part = cleaned_content[start_idx:end_idx]
                return json.loads(json_part)
        
            logger.warning(f"响应内容无法解析为JSON: {cleaned_content[:200]}...")
            return {
                "title": "解析失败",
                "keywords": [],
                "summary": f"无法解析模型响应: {cleaned_content[:100]}...",
                "top_words": []
            }
        
        except json.JSONDecodeError as e:
            # 记录详细错误位置
            logger.error(f"JSON解析错误: {str(e)}，原始内容片段: {cleaned_content[:200]}...")
            return {
            "title": "解析失败",
            "keywords": [],
            "summary": f"JSON解析错误: {str(e)}",
            "top_words": []
            }