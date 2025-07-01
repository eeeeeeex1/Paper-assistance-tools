from typing import List, Dict, Tuple, Optional
import re
import pycorrector
from typing import List, Dict
class ChineseTypoDetector:
    def __init__(self):
        # 初始化错字词典（使用更完善的错字映射）
        self.typo_dict = {
            "正确词1": {"错字1", "错字2"},
            "正确词2": {"错字3", "错字4"},
            # 扩展更多错字对...
        }
        # 预编译正则表达式
        self.typo_pattern = re.compile(r'\b[\u4e00-\u9fa5a-zA-Z]+\b')
    
    def detect_typos(self, text: str) -> List[Dict[str, any]]:
        """检测文本中的错字（返回结构化结果）"""
        typo_results = []
        for match in self.typo_pattern.finditer(text):
            word = match.group(0)
            # 查找错字映射（优化匹配逻辑）
            for correct_word, typos in self.typo_dict.items():
                if word in typos:
                    typo_results.append({
                        "position": match.start(),
                        "length": len(word),
                        "wrong_word": word,
                        "correct_word": correct_word,
                        "suggestions": [correct_word],  # 可扩展多个建议
                        "context": self._get_context(text, match.start(), 20)
                    })
        return typo_results
    
    def highlight_typos(self, text: str, typo_results: List[Dict[str, any]]) -> str:
        """使用HTML标记错字（支持前端富文本展示）"""
        result = text
        # 从后向前处理，避免索引变化
        for typo in sorted(typo_results, key=lambda x: x["position"], reverse=True):
            start = typo["position"]
            end = start + typo["length"]
            # 使用HTML span标记，支持CSS样式
            result = f"{result[:start]}<span class='typo-highlight' data-correct='{typo['correct_word']}'>{result[start:end]}</span>{result[end:]}"
        return result
    
    def _get_context(self, text: str, position: int, length: int) -> str:
        """获取错字上下文（优化边界处理）"""
        start = max(0, position - length)
        end = min(len(text), position + length)
        # 添加上下文省略标记
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        return f"{prefix}{text[start:end]}{suffix}"

    def _highlight_typos(self, content, typo_results):
        """根据检测结果标记文本中的错误"""
        # 这个方法需要根据你的具体需求实现
        # 简单示例：在每个错误单词前后添加标记
        # 实际应用中可能需要更复杂的实现
        result = content
        for typo in reversed(typo_results):  # 从后向前处理，避免索引变化
            start = typo['start']
            end = typo['end']
            result = result[:start] + f"[ERROR]{result[start:end]}[/ERROR]" + result[end:]
        return result
