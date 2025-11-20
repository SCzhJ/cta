# test_text_parser.py
import pytest
import re
from c_web_search.text_parser import TextParser

class TestTextParser:
    @pytest.fixture
    def parser(self):
        return TextParser()

    # ========== extract_between 测试 ==========
    def test_extract_between_basic(self, parser):
        content = "START content END"
        result = parser.extract_between(content, "START", "END")
        assert result == " content "

    def test_extract_between_with_regex(self, parser):
        content = "=== title ==="
        result = parser.extract_between(content, re.compile(r"=+"), re.compile(r"=+"))
        assert result == " title "

    def test_extract_between_no_match_before(self, parser):
        content = "some text"
        result = parser.extract_between(content, "START", "END")
        assert result == ""

    def test_extract_between_no_match_after(self, parser):
        content = "START content"
        result = parser.extract_between(content, "START", "END")
        assert result == ""

    def test_extract_between_before_after_reversed(self, parser):
        content = "END content START"
        result = parser.extract_between(content, "START", "END")
        assert result == ""

    def test_extract_between_empty_content(self, parser):
        result = parser.extract_between("", "A", "B")
        assert result == ""

    def test_extract_between_none_content_raises(self, parser):
        with pytest.raises(ValueError, match="Content cannot be None"):
            parser.extract_between(None, "A", "B")

    def test_extract_between_empty_pattern_raises(self, parser):
        with pytest.raises(ValueError, match="Pattern cannot be empty"):
            parser.extract_between("content", "", "B")

    def test_extract_between_overlapping_patterns(self, parser):
        content = "AA content AA"
        result = parser.extract_between(content, "AA", "AA")
        # 应匹配最左侧起始和最右侧结束
        assert " content " in result

    def test_extract_between_markdown_code_block(self, parser):
        content = '```python\nprint("hello")\n```'
        result = parser.extract_between(content, "```python", "```")
        assert result == '\nprint("hello")\n'

    # ========== search_pattern 测试 ==========
    def test_search_pattern_basic(self, parser):
        content = "prefix TARGET suffix"
        result = parser.search_pattern(content, 0, "prefix", "TARGET", "suffix")
        assert result == ("TARGET", len(content))

    def test_search_pattern_with_regex(self, parser):
        content = "ID:12345;END"
        result = parser.search_pattern(content, 0, 
                                     re.compile(r"ID:"), 
                                     re.compile(r"\d+"), 
                                     re.compile(r";END"))
        assert result == ("12345", len(content))

    def test_search_pattern_start_index(self, parser):
        content = "first START second START TARGET END"
        # 从第二个START开始搜索
        result = parser.search_pattern(content, 10, "START", "TARGET", "END")
        assert result == ("TARGET", len(content))

    def test_search_pattern_no_match_before(self, parser):
        content = "some TARGET END"
        result = parser.search_pattern(content, 0, "START", "TARGET", "END")
        assert result == ("", -1)

    def test_search_pattern_no_match_target(self, parser):
        content = "START some END"
        result = parser.search_pattern(content, 0, "START", "TARGET", "END")
        assert result == ("", -1)

    def test_search_pattern_no_match_after(self, parser):
        content = "START TARGET some"
        result = parser.search_pattern(content, 0, "START", "TARGET", "END")
        assert result == ("", -1)

    def test_search_pattern_start_index_out_of_bounds(self, parser):
        content = "short"
        result = parser.search_pattern(content, 100, "A", "B", "C")
        assert result == ("", -1)

    def test_search_pattern_negative_start_index_raises(self, parser):
        with pytest.raises(ValueError, match="Start index must be non-negative"):
            parser.search_pattern("content", -1, "A", "B", "C")

    def test_search_pattern_none_content_raises(self, parser):
        with pytest.raises(ValueError, match="Content cannot be None"):
            parser.search_pattern(None, 0, "A", "B", "C")

    def test_search_pattern_empty_pattern_raises(self, parser):
        with pytest.raises(ValueError, match="Pattern cannot be empty"):
            parser.search_pattern("content", 0, "", "B", "C")

    def test_search_pattern_iteration(self, parser):
        content = ">>A<< >>B<< >>C<<"
        results = []
        start = 0
        print(parser._compile_pattern(">>"))
        print(parser._compile_pattern(r"[A-Z]"))
        print(parser._compile_pattern("<<"))
        for _ in range(3):
            result, start = parser.search_pattern(content, start, ">>", r"[A-Z]", "<<")
            print(f"result: {result}, start: {start}")
            if start != -1:
                results.append(result)
            else:
                break
        assert results == ["A", "B", "C"]

    def test_search_pattern_target_with_groups(self, parser):
        # 目标模式包含捕获组时，应返回完整匹配
        content = "START 123-456 END"
        result = parser.search_pattern(content, 0, "START", re.compile(r"(\d+)-\d+"), "END")
        assert result == ("123-456", len(content))
