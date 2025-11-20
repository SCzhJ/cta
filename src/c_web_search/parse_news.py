'''
parse news functions: 
    解析新闻文件中的新闻项，返回包含时间、URL和可选的前/后模式的字典列表。

return:
    list[dict[str, str]]: 
        dict必须包含的key有'time'(time如果没有可以是Unknown), 'url', 'crawl_config',
        可选的key有'pattern_before', 'pattern_after'
'''

from pathlib import Path
import re
from crawl4ai import CrawlerRunConfig

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

def parse_newsnow_top(md_file_path: Path) -> list[dict[str, str]]:
    """
    Parse the top Bitcoin news from NewsNow markdown file.
    Returns list of dicts with 'time' and 'url' for each news item.
    """
    
    # Step 1: Read and extract the "Top" section
    with open(md_file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    # Extract between "[ Top ]" section and "## Latest"
    top_section = extract_between(
        full_content, 
        r'\[ Top \]',  # Start after navigation + Follow
        r'\n## Latest'  # End before Latest section
    )
    
    if not top_section:
        print("No top news section found")
        return []
    
    # Step 2: Parse news items line-by-line
    news_items = []
    
    # Pattern to match NewsNow news URLs
    url_pattern = re.compile(r'https://c\.newsnow\.com/A/\d+\?[^)\s]+')
    # Pattern to match time (e.g., "1h", "2h") at end of line
    time_pattern = re.compile(r'(\d{1,2})h$')
    
    for line in top_section.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Look for lines containing a NewsNow URL
        url_match = url_pattern.search(line)
        time_match = time_pattern.search(line)
        
        if url_match and time_match:
            url = url_match.group(0)
            time_str = f"{time_match.group(1)}h"
            
            # Avoid adding duplicate URLs (skip duplicate source lines)
            if not any(item['url'] == url for item in news_items):
                news_items.append({
                    'time': time_str,
                    'url': url,
                    'pattern_before': r'\n#\s{0,5}\w',
                    'pattern_after': r'(.{0,15}\[[^\)]*\([^)]*\).{0,20}\n){5}',
                    'crawl_config': CrawlerRunConfig(
                        verbose=True,
                        # 等待2秒让JavaScript执行完成
                        wait_for="css:body",  # 或者使用 "timeout:3000" 等待3秒
                        # 或者直接在页面执行JS代码
                        js_code="""
                            // 等待重定向完成
                            await new Promise(resolve => setTimeout(resolve, 3000));

                            // 如果页面有跳转逻辑，等待URL变化
                            let attempts = 0;
                            while (window.location.href.includes('newsnow.com') && attempts < 30) {
                                await new Promise(resolve => setTimeout(resolve, 100));
                                attempts++;
                            }
                        """
                    )
                })
    
    return news_items

def parse_newsnow_latest(md_file_path: Path) -> list[dict[str, str]]:
    """
    Parse the latest Bitcoin news from NewsNow markdown file.
    Returns list of dicts with 'time' and 'url' for each news item.
    """
    # Step 1: Extract the "## Latest" section
    with open(md_file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    latest_section = extract_between(full_content, r'## Latest', r'\n####')
    if not latest_section:
        print("No latest news section found")
        return []
    
    # Step 2: Find all lines with NewsNow news URLs
    news_items = []
    news_url_pattern = r'https://c\.newsnow\.com/A/\d+\?[^)\s]+'
    
    for line in latest_section.split('\n'):
        # Skip empty lines
        if not line.strip():
            continue
            
        # Find NewsNow URLs in this line
        url_match = re.search(news_url_pattern, line)
        time_match = re.search(r'(\d{1,2}:\d{2})$', line.strip())
        
        if url_match and time_match:
            news_items.append({
                'time': time_match.group(1),
                'url': url_match.group(0),
                'pattern_before': r'\n#\s{0,5}\w',
                'pattern_after': r'(.{0,5}\[[^\)]*\([^)]*\)\n){5}',
                'crawl_config': CrawlerRunConfig(
                    verbose=True,
                    # 等待2秒让JavaScript执行完成
                    wait_for="css:body",  # 或者使用 "timeout:3000" 等待3秒
                    # 或者直接在页面执行JS代码
                    js_code="""
                        // 等待重定向完成
                        await new Promise(resolve => setTimeout(resolve, 3000));

                        // 如果页面有跳转逻辑，等待URL变化
                        let attempts = 0;
                        while (window.location.href.includes('newsnow.com') && attempts < 30) {
                            await new Promise(resolve => setTimeout(resolve, 100));
                            attempts++;
                        }
                    """
                )
            })
    
    return news_items

def parse_cryptonews_top(md_file_path: Path) -> list[dict[str, str]]:
    """Parse top Bitcoin stories from crypto.news markdown file"""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    # Extract the Top Bitcoin Stories section
    top_section = extract_between(
        full_content,
        r'##  Top Bitcoin Stories',
        r'\n##  Latest Bitcoin News'
    )
    
    if not top_section:
        print("No top stories section found")
        return []
    
    news_items = []
    lines = top_section.split('\n')
    
    # Pattern to match markdown links: [text](url)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    # Pattern to match time: "X days ago" or "X hours ago"
    time_pattern = re.compile(r'(\d+)\s+(day|hour)s?\s+ago', re.IGNORECASE)
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for ### [title](url) pattern
        if line.startswith('###  ') and '](' in line:
            link_match = link_pattern.search(line)
            if link_match:
                url = link_match.group(2)
                
                # Look for time in the next 3 lines
                time_str = "Unknown"
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[j].strip()
                    time_match = time_pattern.search(next_line)
                    if time_match:
                        value = time_match.group(1)
                        unit = time_match.group(2)
                        time_str = f"{value} {unit}{'s' if int(value) > 1 else ''} ago"
                        break
                
                news_items.append({
                    'time': time_str,
                    'url': url,
                    'pattern_before': '\n#',
                    'pattern_after': 'Read more',
                    'crawl_config': CrawlerRunConfig(
                        verbose=True,
                        wait_for="body"  # 等待body元素出现
                    )
                            
                })          
                            
    # print(f"\n✅ Fo        und {len(news_items)} Top Bitcoin Stories\n")
    # print("=" * 60)
    
    # for idx, item in enumerate(news_items, 1):
    #     print(f"{idx}. [{item['time']}] {item['url']}")
    
    return news_items

def parse_cryptonews_latest(md_file_path: Path) -> list[dict[str, str]]:
    """Parse latest Bitcoin news from crypto.news markdown file"""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    # Extract the Latest Bitcoin News section
    latest_section = extract_between(
        full_content,
        r'##  Latest Bitcoin News',
        r'\nShow More'
    )
    
    if not latest_section:
        print("No latest news section found")
        return []
    
    news_items = []
    lines = latest_section.split('\n')
    
    # Pattern to match markdown links
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    # Pattern to match standalone time lines: "X days ago" or "X hours ago"
    time_pattern = re.compile(r'^(\d+)\s+(week|day|hour)s?\s+ago$', re.IGNORECASE)
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for [ Read more - title](url) pattern
        if line.startswith('[ Read more -') and '](' in line:
            link_match = link_pattern.search(line)
            if link_match:
                url = link_match.group(2)
                
                # Look for time in the next 6 lines (timestamp appears ~4-5 lines after)
                time_str = "Unknown"
                for j in range(i + 1, min(i + 7, len(lines))):
                    next_line = lines[j].strip()
                    # Check if this is a standalone time line
                    time_match = time_pattern.match(next_line)
                    if time_match:
                        value = time_match.group(1)
                        unit = time_match.group(2)
                        time_str = f"{value} {unit}s ago"
                        break
                
                # Avoid duplicates
                if not any(item['url'] == url for item in news_items):
                    news_items.append({
                        'time': time_str,
                        'url': url,
                        'pattern_before': '\n#',
                        'pattern_after': 'Read more',
                        'crawl_config': CrawlerRunConfig(
                            verbose=True,
                            wait_for="body"  # 等待body元素出现
                        )
                    })
    
    # print(f"\n✅ Found {len(news_items)} Latest Bitcoin News\n")
    # print("=" * 60)
    
    # for idx, item in enumerate(news_items, 1):
    #     print(f"{idx}. [{item['time']}] {item['url']}")
    
    return news_items

def parse_99bitcoins_latest(md_file_path: Path) -> list[dict[str, str]]:
    """Parse latest Bitcoin news from 99bitcoins_news.md - all items are in one line"""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    # Extract section between "#  Bitcoin (BTC) News Today" and pagination
    news_section = extract_between(
        full_content,
        r'#  Bitcoin \(BTC\) News Today',
        r'\n1 \[2\]'  # Start of pagination
    )
    
    if not news_section:
        print("No news section found")
        return []
    
    news_items = []
    
    # Pattern to capture date and URL from each markdown link block
    # Format: [ ![img](img_url) Title text... Month DD, YYYY By Author ](news_url)
    item_pattern = re.compile(
        r'\[.*?([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}).*?\]\((https://99bitcoins\.com/news/bitcoin-btc/[^)\s]+)\)'
    )
    
    # Find all matches in the entire section at once
    for date, url in item_pattern.findall(news_section):
        news_items.append({
            'time': date,
            'url': url,
            'crawl_config': CrawlerRunConfig(
                verbose=True,
                wait_for="body"  # 等待body元素出现
            )
        })
    
    # Remove duplicates (if any)
    seen_urls = set()
    unique_items = []
    for item in news_items:
        if item['url'] not in seen_urls:
            seen_urls.add(item['url'])
            unique_items.append(item)
    
    # print(f"\n✅ Found {len(unique_items)} Bitcoin News Today\n")
    # print("=" * 60)
    
    # for idx, item in enumerate(unique_items, 1):
    #     print(f"{idx}. [{item['date']}] {item['url']}")
    
    return unique_items

def parse_theblock_latest(md_file_path: Path) -> list[dict[str, str]]:
    """
    Parse the latest crypto news from The Block markdown file.
    Returns list of dicts with 'date' and 'url' for each news item.
    """
    # Step 1: Extract the "## Latest Crypto News" section
    with open(md_file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    # Use extract_between to isolate the news section
    latest_section = extract_between(
        full_content, 
        r'# Latest Crypto News', 
        r'\n  \* Prev'  # End at pagination
    )
    if not latest_section:
        print("No latest news section found")
        return []
    
    # Step 2: Parse each news item using line-by-line detection
    news_items = []
    lines = latest_section.split('\n')
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    for i, line in enumerate(lines):
        # Detect news title lines (start with ## [)
        if line.lstrip().startswith('## ['):
            # Extract URL from markdown link
            link_match = link_pattern.search(line)
            if link_match:
                url = link_match.group(2)
                
                # Find date in the next non-empty line
                date_str = "Unknown"
                for j in range(i + 1, min(i + 3, len(lines))):  # Check next 2 lines
                    next_line = lines[j].strip()
                    if next_line:
                        date_match = re.search(r'([A-Za-z]{3} \d{1,2}, \d{4}, \w{1,2}\:\w{2}\w{1,2} EST)', next_line)
                        if date_match:
                            date_str = date_match.group(1)
                        break
                
                news_items.append({
                    'time': date_str,
                    'url': url,
                    'crawl_config': CrawlerRunConfig(
                        verbose=True,
                        wait_for="body"  # 等待body元素出现
                    )
                })
    
    
    return news_items

# Execute both functions
# if __name__ == "__main__":
#     top_stories = parse_cryptonews_top(Path('logs') / 'news' / 'crypto_news.md')
#     latest_news = parse_cryptonews_latest(Path('logs') / 'news' / 'crypto_news.md')
#     parse_99bitcoins_latest(Path('logs') / 'news' / '99bitcoins_news.md')
    
