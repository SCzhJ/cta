import asyncio
import pytest
import re
from c_web_search.parse_news import *
from pathlib import Path
from c_web_search.crawl_websites import *
from a_utils.file_manager import get_date_str

@pytest.mark.asyncio
async def test_parse_news():
    news_items_newsnow_top = parse_newsnow_top(project_root / 'logs' / 'news' / 'newsnow_news.md')
    news_items_cryptonews_top = parse_cryptonews_top(project_root / 'logs' / 'news' / 'crypto_news.md')

    news_items_newsnow_latest = parse_newsnow_latest(project_root / 'logs' / 'news' / 'newsnow_news.md')
    news_items_cryptonews_latest = parse_cryptonews_latest(project_root / 'logs' / 'news' / 'crypto_news.md')
    news_items_99bitcoins_latest = parse_99bitcoins_latest(project_root / 'logs' / 'news' / '99bitcoins_news.md')
    news_items_theblock_latest = parse_theblock_latest(project_root / 'logs' / 'news' / 'theblock_news.md')
    
    def print_news_items(items, title):
        print(f"\n✅ Found {len(items)} {title}\n")
        print("=" * 60)
        for idx, item in enumerate(items, 1):
            print(f"{idx}. [{item['time']}] {item['url']}")
        # print(items)

    print_news_items(news_items_newsnow_top, "Newsnow Top")
    print_news_items(news_items_cryptonews_top, "Cryptonews Top")
    print_news_items(news_items_newsnow_latest, "Newsnow Latest News")
    print_news_items(news_items_cryptonews_latest, "Cryptonews Latest News")
    print_news_items(news_items_99bitcoins_latest, "99bitcoins Latest News")
    print_news_items(news_items_theblock_latest, "Theblock Latest News")

    # top_news_save_path = project_root / "logs" / "outputs" / get_date_str() / 'news' / 'top-news'
    # if not top_news_save_path.exists():
    #     top_news_save_path.mkdir(parents=True)
    # results = await crawl_websites_and_save(news_items_newsnow_top, top_news_save_path)
    # results = await crawl_websites_and_save(news_items_cryptonews_top, top_news_save_path)

    # latest_news_save_path = project_root / "logs" / "outputs" / get_date_str() / 'news' / 'latest-news'
    # if not latest_news_save_path.exists():
    #     latest_news_save_path.mkdir(parents=True)
