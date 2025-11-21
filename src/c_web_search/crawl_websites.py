from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
import asyncio
from typing import Any, List, Dict
from pathlib import Path
import logging
from re import Pattern
import json

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
from c_web_search.text_parser import extract_between, remove_url

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

async def crawl_websites_and_save(website_urls: List[str], 
                                  save_path: Path,
                                  retry_min_news_length: int=1500,
                                  retry_max_attempts: int=3):
    website_url_dicts = [{'url': url, 'crawl_config': CrawlerRunConfig(verbose=True, wait_for='body')} for url in website_urls]
    results = await crawl_websites(website_url_dicts)
    for url, result in zip(website_urls, results):
        if len(result) < retry_min_news_length:
            crawler_logger.warning(f"News from {url} length {len(result)} is less than {retry_min_news_length}, retry {retry_max_attempts} times")
            for j in range(retry_max_attempts):
                result = await crawl_website(url, website_url_dicts[i]['crawl_config'])
                if len(result) >= retry_min_news_length:
                    break
                else:
                    crawler_logger.warning(f"News from {url} length {len(result)} is still less than {retry_min_news_length}, retry {j+1}/{retry_max_attempts} times")
        website_name = generate_website_name(url)
        save_file = save_path / f"{website_name}.md"
        with open(save_file, "w", encoding="utf-8") as f:
            f.write(result)

async def crawl_websites_parse_and_save(website_url_dicts: List[Dict[str, Any]], 
                                        save_name: str,
                                        save_path: Path, 
                                        save_md_path: Path|None=None,
                                        name_prefix: str="", 
                                        name_add_index: bool=False, 
                                        remove_http_url: bool=False,
                                        retry_min_news_length: int=1500,
                                        retry_max_attempts: int=3):
    '''
    从字典列表中提取URL，爬取并保存到指定路径。
    
    参数:
        website_url_dicts: 每个字典必须包含'url', 'crawl_config'。可选包含'pattern_before', 'pattern_after', 'min_length', 'min_parse_lines'。
            url: 网站url
            crawl_config: CrawlerRunConfig对象，用于配置爬取行为
            pattern_before: 用于提取新闻内容的正则表达式模式，默认为空字符串，可以没有该键
            pattern_after: 用于提取新闻内容的正则表达式模式，默认为空字符串，可以没有该键
            min_length: 提取内容的最小长度，默认为0，可以没有该键
            min_parse_lines: 提取内容的最小行数，默认为0，可以没有该键
        save_name: 保存文件的名称，不包含扩展名
        save_path: 保存JSONL文件的目录路径
        save_md_path: 保存Markdown文件的目录路径，默认为None
        name_prefix: 文件名前缀，默认为空字符串
        name_add_index: 是否在文件名后添加索引，默认为False
        remove_http_url: 是否移除HTTP/HTTPS URL，默认为False
        retry_min_news_length: 重试最小新闻长度，默认为1500
        retry_max_attempts: 重试最大次数，默认为3
    '''
    results = await crawl_websites(website_url_dicts)
    website_urls = [dictionary['url'] for dictionary in website_url_dicts]
    new_results = []
    for i, result in enumerate(results):
        if len(result) < retry_min_news_length:
            crawler_logger.warning(f"News from {website_urls[i]} length {len(result)} is less than {retry_min_news_length}, retry {retry_max_attempts} times")
            for j in range(retry_max_attempts):
                result = await crawl_website(website_urls[i], website_url_dicts[i]['crawl_config'])
                if len(result) >= retry_min_news_length:
                    break
                else:
                    crawler_logger.warning(f"News from {website_urls[i]} length {len(result)} is still less than {retry_min_news_length}, retry {j+1}/{retry_max_attempts} times")
        website_name = name_prefix+generate_website_name(website_urls[i])
        if name_add_index:
            website_name += f"_{i}"
        if 'pattern_before' in website_url_dicts[i].keys() and \
            'pattern_after' in website_url_dicts[i].keys() and \
            'min_length' in website_url_dicts[i].keys() and \
            'min_parse_lines' in website_url_dicts[i].keys():
            result = extract_between(result, 
                                     website_url_dicts[i]['pattern_before'], 
                                     website_url_dicts[i]['pattern_after'], 
                                     inclusive=True, allow_after_pattern_not_found=True, 
                                     min_parse_lines=website_url_dicts[i]['min_parse_lines'], 
                                     min_length=website_url_dicts[i]['min_length'])
        if remove_http_url:
            result = remove_url(result)
        new_results.append(result)
        if save_md_path:
            with open(save_md_path / f"{website_name}_news.md", "w", encoding="utf-8") as f:
                f.write(result)
                crawler_logger.info(f"Successfully saved {website_name}_news.md")
    new_dicts = []
    # save results as jsonl
    with open(save_path / f"{save_name}.jsonl", "w", encoding="utf-8") as f:
        for i, result in enumerate(new_results):
            '''
            to be added: news time calculation and save
            '''
            f.write(json.dumps({"url": website_urls[i], 'time': website_url_dicts[i]['time'], "news": result}, ensure_ascii=False) + "\n")
            new_dicts.append({"url": website_urls[i], 'time': website_url_dicts[i]['time'], "news": result})
        crawler_logger.info(f"Successfully saved {save_name}.jsonl")
    return new_dicts
