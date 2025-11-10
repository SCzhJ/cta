# test_token_tracker.py
import pytest
import logging
from b_provider_adapter.token_tracker import TokenTracker

# 配置日志，确保所有日志器都能输出
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__)
# 确保TokenTracker类中的日志器也能输出日志
# logging.getLogger('b_provider_adapter.token_tracker').setLevel(logging.DEBUG)

def test_logging():
    logger.info("This is an info message")
    logger.warning("This is a warning")
    assert True

def test_token_tracker():
    tracker = TokenTracker()
    tracker.update_deposit()
    
def test_token_tracker_usage():
    tracker = TokenTracker()
    tracker.track_usage("qwen3-max", "alibaba-cn", 100, 200)
    logger.info(tracker.usage_records)

def test_token_tracker_finalize():
    tracker = TokenTracker()
    tracker.update_deposit()
    tracker.track_usage("qwen3-max", "alibaba-cn", 100, 200)
    logger.info(tracker.usage_records)
    tracker.track_usage("kimi-k2-0905-preview", "kimi", 300, 200)
    logger.info(tracker.usage_records)
    tracker.track_usage("qwen-flash", "alibaba-cn", 1000, 200)
    logger.info(tracker.usage_records)
    tracker.track_usage("kimi-k2-0905-preview", "kimi", 150, 200)
    logger.info(tracker.usage_records)
    tracker.track_usage("web_search", "kimi", 0, 0)
    logger.info(tracker.usage_records)
    summary = tracker.get_summary()
    logger.info(summary)
    tracker.finalize()
