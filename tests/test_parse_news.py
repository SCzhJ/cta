import asyncio
import pytest
import re
from c_web_search.parse_news import *
from pathlib import Path
from c_web_search.crawl_websites import *
from a_utils.file_manager import get_date_str

@pytest.mark.asyncio
async def test_parse_news():
    news_items_newsnow_top = parse_newsnow_top(project_root / 'logs' / 'news' / 'newsnow.md')
    news_items_cryptonews_top = parse_cryptonews_top(project_root / 'logs' / 'news' / 'crypto.md')
    news_items_newsnow_latest = parse_newsnow_latest(project_root / 'logs' / 'news' / 'newsnow.md')
    news_items_cryptonews_latest = parse_cryptonews_latest(project_root / 'logs' / 'news' / 'crypto.md')
    news_items_99bitcoins_latest = parse_99bitcoins_latest(project_root / 'logs' / 'news' / '99bitcoins.md')
    news_items_theblock_latest = parse_theblock_latest(project_root / 'logs' / 'news' / 'theblock.md')
    
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

    top_news_save_path = project_root / "logs" / "outputs" / get_date_str() / 'news' / 'top-news-test'
    if not top_news_save_path.exists():
        top_news_save_path.mkdir(parents=True)
    news_items_newsnow_top = news_items_newsnow_top[:5]
    news_items_cryptonews_top = news_items_cryptonews_top[:3]

    latest_news_save_path = project_root / "logs" / "outputs" / get_date_str() / 'news' / 'latest-news-test'
    if not latest_news_save_path.exists():
        latest_news_save_path.mkdir(parents=True)
    news_items_newsnow_latest = news_items_newsnow_latest[:5]
    news_items_cryptonews_latest = news_items_cryptonews_latest[:3]

    relevant_news_save_path = project_root / "logs" / "outputs" / get_date_str() / 'news' / 'relevant-news'
    if not relevant_news_save_path.exists():
        relevant_news_save_path.mkdir(parents=True)
    news_items_99bitcoins_latest = news_items_99bitcoins_latest[:3]
    news_items_theblock_latest = news_items_theblock_latest[:3]

    results = await asyncio.gather(
        crawl_websites_parse_and_save(website_url_dicts=news_items_newsnow_top, 
                                      save_name="newsnow_top",
                                      save_path=top_news_save_path,
                                      save_md_path=top_news_save_path, 
                                      name_prefix="newsnow_top_", 
                                      name_add_index=True, 
                                      remove_http_url=True),
        crawl_websites_parse_and_save(website_url_dicts=news_items_cryptonews_top, 
                                      save_name="cryptonews_top",
                                      save_path=top_news_save_path, 
                                      save_md_path=top_news_save_path,
                                      name_prefix="cryptonews_top_", 
                                      name_add_index=True, 
                                      remove_http_url=True),
        crawl_websites_parse_and_save(website_url_dicts=news_items_newsnow_latest, 
                                      save_name="newsnow_latest",
                                      save_path=latest_news_save_path,
                                      save_md_path=latest_news_save_path, 
                                      name_prefix="newsnow_latest_", 
                                      name_add_index=True, 
                                      remove_http_url=True),
        crawl_websites_parse_and_save(website_url_dicts=news_items_cryptonews_latest, 
                                      save_name="cryptonews_latest",
                                      save_path=latest_news_save_path, 
                                      save_md_path=latest_news_save_path,
                                      name_prefix="cryptonews_latest_", 
                                      name_add_index=True, 
                                      remove_http_url=True),
        crawl_websites_parse_and_save(website_url_dicts=news_items_99bitcoins_latest, 
                                      save_name="99bitcoins_latest",
                                      save_path=relevant_news_save_path, 
                                      save_md_path=relevant_news_save_path,
                                      name_prefix="99bitcoins_latest_", 
                                      name_add_index=True,
                                      remove_http_url=True),
        crawl_websites_parse_and_save(website_url_dicts=news_items_theblock_latest, 
                                      save_name="theblock_latest",
                                      save_path=relevant_news_save_path, 
                                      save_md_path=relevant_news_save_path,
                                      name_prefix="theblock_latest_", 
                                      name_add_index=True,
                                      remove_http_url=True)
    )