# text_parser.py
import re
from typing import Pattern

def compile_pattern(pattern: str | Pattern) -> Pattern:
    """内部辅助方法：将字符串模式编译为正则对象。"""
    if isinstance(pattern, str):
        if not pattern:
            raise ValueError("Pattern cannot be empty")
        return re.compile(pattern)
    return pattern

def extract_between(
    content: str, 
    pattern_before: str | Pattern, 
    pattern_after: str | Pattern,
    inclusive: bool=False,
    allow_after_pattern_not_found: bool=False
) -> str:
    '''
    提取两个模式标记之间的文本内容（不包含after模式）。
    
    参数:
        content: 待解析的文档字符串
        pattern_before: 起始模式（字符串或正则）
        pattern_after: 结束模式（字符串或正则）
        inclusive: 是否包含pattern_before模式本身，默认为False
        allow_after_pattern_not_found: 是否允许未找到结束模式，默认为False
        
    返回:
        两模式之间的文本；未匹配返回空字符串
        
    异常:
        ValueError: 当content为None或pattern为空时抛出
    '''
    if content is None:
        raise ValueError("Content cannot be None")
    
    before_regex = compile_pattern(pattern_before)
    after_regex = compile_pattern(pattern_after)
    
    # 搜索起始模式
    before_match = before_regex.search(content)
    if not before_match:
        return ""
    
    # 从起始模式之后搜索结束模式
    start_pos = before_match.end()
    after_match = after_regex.search(content, start_pos)
    if not after_match:
        if allow_after_pattern_not_found:
            return content[before_match.start():]
        return ""
    
    # 提取区间文本
    end_pos = after_match.start()
    if inclusive:
        return content[before_match.start():end_pos]
    else:
        return content[start_pos:end_pos]
