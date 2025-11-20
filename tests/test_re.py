import asyncio
import pytest
import re
from c_web_search.parse_news import *
from pathlib import Path
from c_web_search.crawl_websites import *
from a_utils.file_manager import get_date_str

def test_re_patterns():
    print()
    file_path = project_root / 'logs' / 'outputs' / '2025-11-20' / 'news' / 'c_0_news.md'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(content)
    pattern = r'(.{0,5}\[[^\)]*\([^)]*\)\n){5}'
    pattern = re.compile(pattern)
    # matches = pattern.search(content)
    matches = pattern.findall(content)
    print("="*20 + "match" + "="*20)
    print(matches)

