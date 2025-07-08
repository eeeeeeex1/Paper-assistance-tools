import re
import logging
import io
from typing import List, Dict, Tuple, Set, Union  # 补充 Tuple 等的导入
from collections import defaultdict
import pycorrector
from pycorrector import Corrector  # 导入Corrector类


logger = logging.getLogger(__name__)
# 定义错字结果的类型
TypoResult = Dict[str, Union[int, str, List[str]]]

class Typo_Detection:
    def __init__(self):
        """初始化中文错字检测器，加载多维度错字字典"""
        self.corrector = Corrector()
        #self.corrector = pycorrector
        # 1. 同音字错字字典 (正确词: 错字集合)
        self.homophone_typos = {
            "安装": {"按装"}, "必须": {"必需"}, "部署": {"布署"}, "策略": {"策论"},
            "产生": {"产生"}, "纯粹": {"纯朴"}, "凑合": {"凑和"}, "粗犷": {"粗旷"},
            "妨碍": {"防碍"}, "辐射": {"幅射"}, "寒暄": {"寒喧"}, "即使": {"既使"},
            "家具": {"家俱"}, "矫揉造作": {"娇揉造作"}, "痉挛": {"痉孪"}, "竣工": {"峻工"},
            "瞭望": {"了望"}, "明信片": {"名信片"}, "迫不及待": {"迫不急待"}, 
            "一如既往": {"一如继往"}, "再接再厉": {"再接再励"}, "坐镇": {"坐阵"},
            "综合征": {"综合症"}, "松弛": {"松驰"}, "迁徙": {"迁徒"}, "提纲": {"题纲"},
            "错误": {"错吴"}, "已经": {"己经"}, "再接再厉": {"再接再励"},
            "防御": {"妨御"}, "措施": {"措失"}
        }
        
        # 2. 形似字错字字典
        self.similar_shape_typos = {
           "己": {"已", "巳"}, "戊": {"戌", "戍"}, "祗": {"祇", "衹", "袛"},
            "菅": {"管"}, "赢": {"羸"}, "汆": {"氽"}, "丐": {"丏"}, "壸": {"壶"},
            "舂": {"春"}, "惴": {"湍", "端"}, "崇": {"祟"}, "斡": {"乾", "翰"},
            "膺": {"赝"}, "弋": {"戈"}, "祓": {"祛"}, "谄媚": {"馅媚"}, "针灸": {"针炙"},
            "如火如荼": {"如火如茶"}, "未来": {"未耒"}, "治理": {"冶理"}, "己巳": {"已巳"},
            "分辨": {"分辩"}, "谥号": {"谥好"}
        }
        
        # 3. 常见搭配错误
        self.collocation_typos = {
            "的": {"得", "地"}, "做": {"作"}, "作": {"做"}, "他": {"她", "它"},
            "她": {"他", "它"}, "它": {"他", "她"}, "再": {"在"}, "在": {"再"},
            "以": {"已"}, "已": {"以"}, "渡": {"度"}, "度": {"渡"}, "合": {"和"},
            "和": {"合"}, "象": {"像", "相"}, "像": {"象", "相"}, "相": {"象", "像"},
            "分": {"份"}, "份": {"分"}, "必须": {"必需"}, "需要": {"须要"}, "反映": {"反应"},
            "其他": {"其它"}, "制定": {"制订"}
        }
        
        # 4. 构建综合错字字典 (错字: 正确词集合)
        self.typo_dict = defaultdict(set)
        for correct, typos in {
            **self.homophone_typos,
            **self.similar_shape_typos,
            **self.collocation_typos
        }.items():
            for typo in typos:
                self.typo_dict[typo].add(correct)
        
        # 5. 编译正则表达式 (匹配中文、英文、数字及部分常用标点)
        self.typo_pattern = re.compile(r'[\u4e00-\u9fa5a-zA-Z0-9，。、？！：；,.!?;:]+')
    
    def _get_context(self, content: str, start: int, length: int = 20) -> str:
        """获取错字上下文，标记错误位置"""
        try:
            if not content or start < 0 or start >= len(content):
                return ""
                
            half_length = length // 2
            start_context = max(0, start - half_length)
            end_context = min(len(content), start + half_length)
            
            context = content[start_context:end_context]
            typo_pos = start - start_context
            marker = "[" + "~" * min(half_length, len(context) - typo_pos) + "]"
            
            return f"{context[:typo_pos]}{marker}{context[typo_pos+1:]}"
        except Exception as e:
            logger.error(f"get updown fail: {str(e)}")
            return "[上下文获取失败]"
    
    def _detect_typos(self, content: str) -> List[Dict]:
        """优化错字检测性能，减少冗余计算"""
        logger.info(f"开始检测文本，长度: {len(content)}")
        """结合自定义词典和pycorrector的错字检测"""

        results = []
    
        try:
            # 1. 使用Corrector实例进行纠错
            details = self.corrector.detect(content)
            corrected_text = self.corrector.correct(content)
            
            # 处理检测结果
            for item in details:
                if item:
                    start, end, wrong, correct = item
                    results.append({
                        'position': start,
                        'wrong_word': wrong,
                        'length': len(wrong),
                        'suggestions': [correct],
                        'context': self._get_context(content, start),
                        'type': 'pycorrector'
                    })
        except Exception as e:
            logger.error(f"PyCorrector检测错误: {str(e)}")
            # fallback到自定义检测
            results = self._detect_typos_with_custom_dict(content)
        
        # 2. 使用自定义词典检测专业领域错字
        for word, correct_list in self.typo_dict.items():
            pos = 0
            while True:
                pos = content.find(word, pos)
                if pos == -1:
                    break
                # 检查是否未被pycorrector检测到
                is_duplicate = any(
                    r['position'] <= pos < r['position'] + r['length'] 
                    for r in results
                )
                if not is_duplicate:
                    results.append({
                        'position': pos,
                        'wrong_word': word,
                        'length': len(word),
                        'suggestions': list(correct_list),
                        'context': self._get_context(content, pos),
                        'type': self._get_error_type(word)
                    })
                pos += 1
        
        # 3. 合并结果
        results = self._merge_typo_results(results)
        return results
    
    def _merge_typo_results(self, results: List[Dict]) -> List[Dict]:
        """按位置合并重复的错字检测结果"""
        if not results:
            return []
            
        # 按位置排序
        sorted_results = sorted(results, key=lambda x: x['position'])
        
        # 合并重叠结果（后一个结果覆盖前一个）
        merged = []
        last_pos = -1
        for result in sorted_results:
            if result['position'] > last_pos:
                merged.append(result)
                last_pos = result['position'] + result['length']
                
        return merged
    
    def _get_error_type(self, word):
        if word in self.homophone_typos:
            return 'homophone'
        elif word in self.similar_shape_typos:
            return 'similar_shape'
        return 'collocation'
    
    def _detect_typos_with_custom_dict(self, content: str) -> List[Dict]:
        """仅使用自定义错字词典进行检测（PyCorrector失败时的备用方案）"""
        logger.info("使用自定义词典进行错字检测")
        results = []
    
        # 1. 构建错字长度索引（从长到短检测，避免短错字覆盖长错字）
        typo_lengths = sorted(set(len(word) for word in self.typo_dict.keys()), reverse=True)
    
        # 2. 按长度从长到短检测错字
        for length in typo_lengths:
            # 生成匹配指定长度的正则表达式
            pattern = rf'(\w{{{length}}})'
            for match in re.finditer(pattern, content):
                word = match.group(1)
                if word in self.typo_dict:
                    position = match.start()
                    results.append({
                    'position': position,
                    'wrong_word': word,
                    'length': len(word),
                    'suggestions': list(self.typo_dict[word]),
                    'context': self._get_context(content, position),
                    'type': self._get_error_type(word)
                    })
                    logger.debug(f"自定义词典检测到错字: '{word}'，位置: {position}")
    
        # 3. 处理长度为1的错字（单独处理）
        for match in re.finditer(r'(\w)', content):
            word = match.group(1)
            if word in self.typo_dict and len(word) == 1:
                position = match.start()
                results.append({
                'position': position,
                'wrong_word': word,
                'length': 1,
                'suggestions': list(self.typo_dict[word]),
                'context': self._get_context(content, position),
                'type': self._get_error_type(word)
                })
    
        # 4. 按位置排序结果
        if results:
            results.sort(key=lambda x: x['position'])
    
        logger.info(f"自定义词典检测完成，共发现 {len(results)} 个错字")
        return results