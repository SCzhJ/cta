from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
import asyncio
from typing import Any, List, Dict
from pathlib import Path
import logging
from re import Pattern

project_root = None
for parent in [Path.cwd(), *Path.cwd().parents]:
    if (parent / "pyproject.toml").exists():
        project_root = parent
        break
if project_root is None:
    raise FileNotFoundError("pyproject.toml 未找到，无法确定项目根目录")
import sys
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
from c_web_search.text_parser import extract_between

crawler_logger = logging.getLogger("WebsiteCrawler")
def verify_url(url: str) -> bool:
    if url.startswith("http://") or url.startswith("https://"):
        return True
    return False

def generate_website_name(url: str):
    # 提取域名部分并去掉www前缀
    website_name = url.split("://")[1].split("/")[0]
    if website_name.startswith("www."):
        website_name = website_name[4:]
    website_name = website_name.split(".")[0]
    
    return website_name

async def crawl_website(url: str, crawl_config: CrawlerRunConfig) -> str:
    if not verify_url(url):
        raise ValueError(f"Invalid URL: {url}")
    try:
        # async with AsyncWebCrawler() as crawler:
        #     result = await crawler.arun(url=url)
        # return result.markdown
        # 配置等待JavaScript重定向完成
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                config=crawl_config
            )

            # 检查最终URL
            crawler_logger.info(f"最终URL: {result.redirected_url}")
            crawler_logger.info(f"内容长度: {len(result.markdown)}")
            return result.markdown
    except Exception as e:
        raise RuntimeError(f"Error crawling {url}: {e}")
    
async def crawl_websites(website_url_dicts: List[Dict[str, Any]]) -> List[str]:
    tasks = [crawl_website(url_dict['url'], url_dict['crawl_config']) for url_dict in website_url_dicts]
    return await asyncio.gather(*tasks)

async def crawl_websites_and_save(website_url_dicts: List[Dict[str, Any]], save_path: Path, name_prefix: str="", name_add_index: bool=False):
    '''
    从字典列表中提取URL，爬取并保存到指定路径。
    
    参数:
        website_url_dicts: 每个字典必须包含'url', 'crawl_config'。可选包含'pattern_before', 'pattern_after'。
            url: 网站url
            crawl_config: CrawlerRunConfig对象，用于配置爬取行为
            pattern_before: 用于提取新闻内容的正则表达式模式，默认为空字符串
            pattern_after: 用于提取新闻内容的正则表达式模式，默认为空字符串
        save_path: 保存Markdown文件的目录路径
        name_prefix: 文件名前缀，默认为空字符串
        name_add_index: 是否在文件名后添加索引，默认为False
    '''
    results = await crawl_websites(website_url_dicts)
    website_urls = [dictionary['url'] for dictionary in website_url_dicts]
    for i, result in enumerate(results):
        website_name = name_prefix+generate_website_name(website_urls[i])
        if name_add_index:
            website_name += f"_{i}"
        if 'pattern_before' in website_url_dicts[i].keys() and 'pattern_after' in website_url_dicts[i].keys():
            result = extract_between(result, website_url_dicts[i]['pattern_before'], website_url_dicts[i]['pattern_after'], inclusive=True, allow_after_pattern_not_found=True)
        with open(save_path / f"{website_name}_news.md", "w", encoding="utf-8") as f:
            f.write(result)
            crawler_logger.info(f"Successfully saved {website_name}_news.md")
    return results
