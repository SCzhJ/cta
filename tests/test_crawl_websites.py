import asyncio
import pytest
from a_utils.config_setup import get_project_root
from c_web_search.crawl_websites import *
from c_web_search.parse_news import *
import logging
import sys
import json

# 配置日志，方便调试
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
project_root = get_project_root()
logger.info(f"Project root: {project_root}")
sys.path.append(str(project_root))

# @pytest.mark.asyncio
# async def test_website_crawler():
#     with open(project_root / "configs" / "search_websites.json", "r", encoding="utf-8") as f:
#         websites = json.load(f)
#     bitcoin_news_websites = list(websites["bitcoin news"]) 
#     websites_dicts = []
#     for site in bitcoin_news_websites:
#         websites_dicts.append({
#             'url': site,
#             'crawl_config': CrawlerRunConfig(
#                 verbose=True,
#                 wait_for='body'
#             )
#         })
#     logger.info(f"Bitcoin news websites: {bitcoin_news_websites}")
#     save_path = project_root / "logs" / "news"
#     results = await crawl_websites_and_save(websites_dicts, save_path)

@pytest.mark.asyncio
async def test_crawl_specific_site():
    url = "https://www.theblock.co/data/on-chain-metrics/bitcoin"
    crawl_config = CrawlerRunConfig(
        verbose=True,
        wait_for='body'
    )
    results = await crawl_websites_and_save([{'url': url, 'crawl_config': crawl_config}], project_root / "logs" / "news")

# @pytest.mark.asyncio
# async def test_website_redirect_crawl():
#     website_url_dicts = parse_newsnow_top(project_root / "logs" / "news" / "newsnow_news.md")
#     website_url_dict = website_url_dicts[0]
#     save_path = project_root / "logs" / "news"
#     results = await crawl_websites_and_save([website_url_dict], save_path)