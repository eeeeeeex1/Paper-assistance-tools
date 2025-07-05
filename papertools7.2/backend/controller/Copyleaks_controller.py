import logging
import time
import requests
import os
from typing import Dict, List
from datetime import datetime
from config.logging_config import logger

class CopyleaksService:
    def __init__(self):
        self.api_key = None
        self.api_email = None
        self.auth_base = "https://id.copyleaks.com"  # 认证服务基础URL
        self.api_base = "https://api.copyleaks.com/v3"  # API服务基础URL
        self.access_token = None
        self.token_expiry = 0
        self.request_limit = 200  # 每分钟请求限制（根据套餐调整）
        self.request_count = 0
        self.last_request_time = time.time()
        self.session = requests.Session()
        self.min_interval = 0.3  # 最小请求间隔（秒）
    
    def set_api_key(self, api_key, api_email):
        """设置Copyleaks API凭证"""
        self.api_key = api_key
        self.api_email = api_email
        logger.info("已设置Copyleaks API凭证")
    
    def _get_access_token(self):
        """获取并缓存访问令牌"""
        current_time = time.time()
        
        # 检查令牌是否存在且未过期（提前60秒刷新）
        if self.access_token and self.token_expiry > current_time + 60:
            return self.access_token
        
        logger.info("获取新的Copyleaks访问令牌")
        auth_url = f"{self.auth_base}/connect/token"  # 正确的认证端点
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.api_email,
            "client_secret": self.api_key
        }

        try:
            response = self.session.post(auth_url, data=payload)
            response.raise_for_status()
            token_data = response.json()
            
            logger.debug(f"认证响应: {token_data}")
            
            self.access_token = token_data["access_token"]
            
            # 计算令牌过期时间
            if "expires_in" in token_data:
                self.token_expiry = current_time + token_data["expires_in"] - 60  # 提前60秒过期
            else:
                # 默认设置为1小时后过期
                logger.warning("认证响应中未找到过期时间，默认设置为1小时后")
                self.token_expiry = current_time + 3600
                
            # 更新会话头
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            })
            
            logger.info("成功获取Copyleaks访问令牌")
            return self.access_token
        except KeyError as e:
            logger.error(f"认证响应格式错误，缺少必要字段: {e}")
            logger.error(f"完整响应: {token_data}")
            raise
        except Exception as e:
            logger.error(f"获取Copyleaks访问令牌失败: {str(e)}")
            raise

    def check_plagiarism(self, text, title="", language="auto", num_articles=10, is_ai_content=False):
        """
        通过Copyleaks API进行查重（支持AI内容检测）
        :param is_ai_content: 是否检测AI生成内容
        """
        # 确保API凭证已设置
        if not self.api_key or not self.api_email:
            logger.error("未设置Copyleaks API凭证")
            return {"error": "auth_error", "message": "未设置API凭证"}
        
        # 频率控制
        current_time = time.time()
        if current_time - self.last_request_time > 60:
            self.request_count = 0
            self.last_request_time = current_time
        
        if self.request_count >= self.request_limit:
            logger.warning(f"达到Copyleaks请求频率限制({self.request_limit}次/分钟)，请稍后再试")
            return {"error": "rate_limit", "message": "请求过于频繁，请稍后再试"}
        
        # 间隔控制
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.request_count += 1
        self.last_request_time = current_time
        
        try:
            # 获取访问令牌
            self._get_access_token()
            
            logger.info('begin CopyleaksService check')
            # 构建请求参数
            payload = {
                "content": text,
                "properties": {
                    "title": title,
                    "language": language,  # 自动检测或指定语种
                    "scanning": {
                        "internet": True,
                        "publications": True,
                        "submissions": True
                    },
                    "aiDetection": {
                        "enabled": is_ai_content
                    }
                }
            }
            
            logger.info('begin submit request check')
            # 使用正确的API端点
            submit_url = f"{self.api_base}/education/check-by-text"
            logger.info(f'submit_url: {submit_url}')
            
            submit_response = self.session.post(submit_url, json=payload)
            logger.info(f'response status code: {submit_response.status_code}')
            logger.info(f'response text: {submit_response.text}')
            
            submit_response.raise_for_status()
            response_data = submit_response.json()
            scan_id = response_data["id"]
            logger.info(f"Copyleaks任务提交成功，ScanID: {scan_id}")
            
            # 等待任务完成（轮询机制）
            result = self._poll_job_status(scan_id, max_attempts=30, poll_interval=3)
            if not result:
                return {"error": "timeout", "message": "查重任务超时"}
            
            # 获取完整结果
            report_url = f"{self.api_base}/education/results/{scan_id}"
            report_response = self.session.get(report_url)
            report_response.raise_for_status()
            report_data = report_response.json()
            
            # 解析结果
            return self._parse_copyleaks_response(report_data)
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Copyleaks API错误 {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            if e.response.status_code == 401:
                # 尝试刷新令牌并重试
                try:
                    self.access_token = None
                    self._get_access_token()
                    return self.check_plagiarism(text, title, language, num_articles, is_ai_content)
                except:
                    return {"error": "auth_error", "message": "认证失败，请检查API凭证"}
            elif e.response.status_code == 429:
                return {"error": "rate_limit", "message": "请求频率过高，请稍后再试"}
            return {"error": "api_error", "message": error_msg}
        except Exception as e:
            logger.error(f"Copyleaks查重异常: {str(e)}", exc_info=True)
            return {"error": "unknown_error", "message": f"查重失败: {str(e)}"}
    
    def _poll_job_status(self, scan_id, max_attempts=30, poll_interval=3):
        """轮询获取任务状态（使用教育API的正确端点）"""
        for attempt in range(max_attempts):
            time.sleep(poll_interval)
            status_url = f"{self.api_base}/education/status/{scan_id}"
            response = self.session.get(status_url)
            
            if response.status_code == 200:
                result = response.json()
                status = result["status"]
                logger.info(f"Scan {scan_id} 状态: {status}")
                
                if status == "completed":
                    return result
                elif status in ["failed", "error"]:
                    error_message = result.get("error", "未知错误")
                    logger.error(f"Copyleaks任务失败: {error_message}")
                    return None
            elif response.status_code == 404:
                logger.warning(f"Copyleaks任务不存在: {scan_id}")
                return None
        
        logger.warning(f"Copyleaks任务轮询超时，ScanID: {scan_id}")
        return None
    
    def _parse_copyleaks_response(self, response):
        """解析Copyleaks API响应并统一格式"""
        try:
            # 总体相似度（使用百分比）
            overall_similarity = response.get("summary", {}).get("similarity", 0)
            
            # 相似来源
            sources = response.get("results", [])
            comparison_results = []
            for source in sources:
                comparison_results.append({
                    "article_title": source.get("title", "未知标题"),
                    "similarity_rate": round(source.get("similarity", 0), 2),
                    "url": source.get("source", {}).get("url", ""),
                    "source": source.get("source", {}).get("type", "未知来源"),
                    "ai_confidence": source.get("aiDetection", {}).get("confidence", 0)
                })
            
            # AI内容检测结果
            ai_result = response.get("aiDetection", {})
            ai_confidence = ai_result.get("confidence", 0)
            ai_classification = ai_result.get("classification", "未知")
            
            return {
                "comprehensive_similarity": round(overall_similarity, 2),
                "paper_title": response.get("title", ""),
                "comparison_results": comparison_results,
                "num_articles": len(sources),
                "using_api": True,
                "api_provider": "Copyleaks",
                "ai_detection": {
                    "confidence": round(ai_confidence, 2),
                    "classification": ai_classification
                }
            }
        except Exception as e:
            logger.error(f"解析Copyleaks响应失败: {str(e)}")
            return {
                "comprehensive_similarity": 0,
                "paper_title": "",
                "comparison_results": [],
                "num_articles": 0,
                "using_api": True,
                "api_provider": "Copyleaks",
                "ai_detection": {
                    "confidence": 0,
                    "classification": "未知"
                }
            }